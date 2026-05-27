"""
productor.py — Adquisición serial y publicación MQTT
=====================================================
Ruta 8. pySerial + MQTT — Opción A

Descripción del pipeline:
    ESP32 (fotoresistencia + LED)
        │ USB Serial (115200 baud)
        ▼
    [Este script — productor.py]
        │ Lee y valida la línea serial
        │ Publica en dos tópicos MQTT:
        │   · sensor/luz   → valor numérico de la fotoresistencia (0–4095)
        │   · sensor/led   → estado del LED ('0' o '1')
        │ Se suscribe a:
        │   · led/control  → reenvía comandos al ESP32 por serial
        ▼
    Broker MQTT local (Mosquitto en VM Linux)

Formato serial esperado desde el ESP32:
    "LUZ:<valor>,LED:<estado>\n"
    Ejemplo: "LUZ:2048,LED:0\n"

Dependencias:
    pip install pyserial paho-mqtt
"""

import serial
import time
import paho.mqtt.client as mqtt

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

PUERTO_SERIAL  = "COM3"       # Cambiar según el puerto asignado al ESP32
BAUDRATE       = 115200
TIMEOUT_SERIAL = 2

BROKER_MQTT    = "172.18.128.44"   # IP de tu VM Linux con Mosquitto
PUERTO_MQTT    = 1883
KEEPALIVE      = 60

TOPICO_LUZ     = "sensor/luz"
TOPICO_LED     = "sensor/led"
TOPICO_CONTROL = "led/control"     # ← tópico que escucha para controlar el LED


# ─── FUNCIONES ────────────────────────────────────────────────────────────────

def conectar_serial(puerto: str, baudrate: int, timeout: int) -> serial.Serial | None:
    """
    Abre la conexión serial con el ESP32.

    Parámetros
    ----------
    puerto   : nombre del puerto COM (Windows) o /dev/ttyUSB0 (Linux)
    baudrate : velocidad en baudios, debe coincidir con Serial.begin() del ESP32
    timeout  : segundos máximos de espera para recibir una línea completa

    Retorna
    -------
    objeto serial.Serial abierto, o None si falló
    """
    try:
        conexion = serial.Serial(puerto, baudrate, timeout=timeout)
        time.sleep(2)  # El ESP32 reinicia al abrirse el puerto; esperar estabilización
        print(f"[SERIAL] Conectado a {puerto} @ {baudrate} baud")
        return conexion
    except serial.SerialException as e:
        print(f"[ERROR SERIAL] No se pudo abrir {puerto}: {e}")
        return None


def conectar_mqtt(broker: str, puerto: int, keepalive: int,
                  conexion_serial: serial.Serial | None) -> mqtt.Client:
    """
    Crea y conecta un cliente MQTT al broker.

    Además de publicar datos del ESP32, este cliente se suscribe a
    'led/control' y reenvía los comandos recibidos al ESP32 por serial,
    cerrando el ciclo: controlador_led.py → MQTT → productor → ESP32.

    Parámetros
    ----------
    broker          : dirección o IP del broker MQTT
    puerto          : puerto TCP del broker
    keepalive       : intervalo de ping de mantenimiento en segundos
    conexion_serial : puerto serial abierto hacia el ESP32

    Retorna
    -------
    cliente mqtt.Client ya conectado con loop en hilo de fondo
    """
    cliente = mqtt.Client()

    # ── Callback: conexión establecida ────────────────────────────────────────
    def al_conectar(client, userdata, flags, rc):
        codigos = {
            0: "Conexión aceptada",
            1: "Versión de protocolo incorrecta",
            2: "Identificador de cliente rechazado",
            3: "Servidor no disponible",
            4: "Usuario o contraseña incorrectos",
            5: "No autorizado",
        }
        mensaje = codigos.get(rc, f"Código desconocido: {rc}")
        if rc == 0:
            print(f"[MQTT] Conectado a {broker}:{puerto} — {mensaje}")
            # Suscribirse a led/control para recibir comandos del controlador
            client.subscribe(TOPICO_CONTROL)
            print(f"[MQTT] Suscrito a: {TOPICO_CONTROL}")
        else:
            print(f"[MQTT ERROR] Fallo de conexión — {mensaje}")

    # ── Callback: desconexión inesperada ──────────────────────────────────────
    def al_desconectar(client, userdata, rc):
        if rc != 0:
            print(f"[MQTT] Desconexión inesperada (código {rc}). Reintentando...")

    # ── Callback: mensaje recibido en led/control ─────────────────────────────
    def al_recibir_mensaje(client, userdata, msg):
        """
        Recibe comandos de controlador_led.py y los reenvía al ESP32 por serial.

        controlador_led.py publica '1' o '0' en led/control
        → este callback escribe ese byte directamente al ESP32
        → el ESP32 lo lee con Serial.read() y enciende o apaga el LED
        """
        if msg.topic == TOPICO_CONTROL:
            try:
                comando = msg.payload.decode("utf-8").strip()
                if comando in ("0", "1"):
                    if conexion_serial and conexion_serial.is_open:
                        conexion_serial.write(comando.encode("utf-8"))
                        accion = "ENCENDER" if comando == "1" else "APAGAR"
                        print(f"[SERIAL → ESP32] Comando recibido: '{comando}' → {accion} LED")
                    else:
                        print("[ADVERTENCIA] Comando recibido pero serial no disponible")
                else:
                    print(f"[ADVERTENCIA] Comando desconocido en {TOPICO_CONTROL}: '{comando}'")
            except Exception as e:
                print(f"[ERROR] No se pudo reenviar comando al ESP32: {e}")

    cliente.on_connect    = al_conectar
    cliente.on_disconnect = al_desconectar
    cliente.on_message    = al_recibir_mensaje  # ← nuevo callback

    try:
        cliente.connect(broker, puerto, keepalive)
        cliente.loop_start()   # Hilo de fondo: mantiene conexión y despacha callbacks
    except Exception as e:
        print(f"[ERROR MQTT] No se pudo conectar al broker: {e}")

    return cliente


def parsear_linea(linea_raw: bytes) -> dict | None:
    """
    Decodifica y valida una línea serial del ESP32.

    Formato esperado: "LUZ:<entero>,LED:<0 o 1>\\n"
    Ejemplo real:     "LUZ:2048,LED:0\\n"

    Parámetros
    ----------
    linea_raw : bytes leídos del puerto serial

    Retorna
    -------
    dict con claves 'luz' (int) y 'led' (int), o None si la línea es inválida
    """
    try:
        linea = linea_raw.decode("utf-8").strip()

        if not linea:
            return None

        if "," not in linea or "LUZ:" not in linea or "LED:" not in linea:
            print(f"[PARSE] Formato inesperado: '{linea}'")
            return None

        partes = linea.split(",")
        if len(partes) != 2:
            print(f"[PARSE] Número de campos incorrecto: '{linea}'")
            return None

        valor_luz = int(partes[0].split(":")[1])
        valor_led = int(partes[1].split(":")[1])

        # Validar rangos físicos del ESP32
        if not (0 <= valor_luz <= 4095):
            print(f"[PARSE] Valor de luz fuera de rango: {valor_luz}")
            return None

        if valor_led not in (0, 1):
            print(f"[PARSE] Estado de LED inválido: {valor_led}")
            return None

        return {"luz": valor_luz, "led": valor_led}

    except (UnicodeDecodeError, ValueError, IndexError) as e:
        print(f"[PARSE ERROR] No se pudo interpretar la línea: {e}")
        return None


def publicar_datos(cliente: mqtt.Client, datos: dict) -> None:
    """
    Publica los datos del sensor en los tópicos MQTT correspondientes.

    Parámetros
    ----------
    cliente : cliente MQTT ya conectado
    datos   : dict con claves 'luz' y 'led'
    """
    payload_luz = str(datos["luz"])
    payload_led = str(datos["led"])

    resultado_luz = cliente.publish(TOPICO_LUZ, payload_luz)
    resultado_led = cliente.publish(TOPICO_LED, payload_led)

    if resultado_luz.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"[MQTT ERROR] Fallo al publicar en {TOPICO_LUZ}")
    if resultado_led.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"[MQTT ERROR] Fallo al publicar en {TOPICO_LED}")

    print(f"[PUBLICADO] {TOPICO_LUZ}={payload_luz}  |  {TOPICO_LED}={payload_led}")


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    """
    Bucle principal del productor.

    Flujo:
      1. Abre el puerto serial con el ESP32.
      2. Conecta al broker MQTT y se suscribe a led/control.
      3. Lee líneas del ESP32 indefinidamente.
      4. Parsea y valida cada línea.
      5. Publica los datos válidos en sensor/luz y sensor/led.
      6. Si llega un comando en led/control, lo reenvía al ESP32 por serial.
    """
    print("=" * 55)
    print("  PRODUCTOR IoT — ESP32 → pySerial → MQTT")
    print(f"  Publica : {TOPICO_LUZ} | {TOPICO_LED}")
    print(f"  Escucha : {TOPICO_CONTROL}  (reenvía al ESP32)")
    print("=" * 55)

    # 1. Abrir conexión serial con el ESP32
    esp = conectar_serial(PUERTO_SERIAL, BAUDRATE, TIMEOUT_SERIAL)
    if esp is None:
        print("[FATAL] No se pudo abrir el puerto serial. Verifique la conexión USB.")
        return

    # 2. Conectar al broker MQTT pasando la conexión serial para el callback
    cliente_mqtt = conectar_mqtt(BROKER_MQTT, PUERTO_MQTT, KEEPALIVE, esp)

    # 3. Bucle de lectura y publicación
    print("\n[INFO] Iniciando lectura. Presione Ctrl+C para detener.\n")
    try:
        while True:
            try:
                linea_raw = esp.readline()
            except serial.SerialException as e:
                print(f"[ERROR SERIAL] Pérdida de conexión: {e}")
                print("[INFO] Esperando 3 segundos antes de reintentar...")
                time.sleep(3)
                continue

            if not linea_raw:
                continue

            datos = parsear_linea(linea_raw)
            if datos is None:
                continue

            try:
                publicar_datos(cliente_mqtt, datos)
            except Exception as e:
                print(f"[ERROR MQTT] No se pudo publicar: {e}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupción del usuario. Cerrando conexiones...")

    finally:
        esp.close()
        cliente_mqtt.loop_stop()
        cliente_mqtt.disconnect()
        print("[INFO] Conexiones cerradas. Programa terminado.")


if __name__ == "__main__":
    main()