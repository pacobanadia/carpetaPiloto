"""
controlador_led.py — Interfaz de control del LED por MQTT
=========================================================
Ruta 8. pySerial + MQTT — Adaptación propia
Autor: [Nombre del estudiante]

Propósito (adaptación propia del tutorial base):
    Este script es la adaptación propia requerida por la actividad. Va más
    allá de los ejemplos del tutorial porque:

      1. Implementa un menú interactivo en consola (no solo una publicación fija).
      2. Combina publicación (led/control) con suscripción (sensor/luz) en un
         mismo cliente, mostrando retroalimentación del sensor en tiempo real.
      3. Incluye un modo automático: el LED se enciende solo si la luz es baja
         (fotoresistencia < UMBRAL_OSCURIDAD), simulando un sensor de presencia
         o un sistema de iluminación inteligente simple.

Pipeline de este script:
    Usuario (teclado) → controlador_led.py → MQTT → ESP32 (led/control)
    ESP32 (sensor/luz) → MQTT → controlador_led.py (muestra retroalimentación)

Tópicos:
    - led/control  → publica '1' (encender) o '0' (apagar) hacia el ESP32
    - sensor/luz   → se suscribe para mostrar el nivel de luz actual

Dependencias:
    pip install paho-mqtt
"""

import paho.mqtt.client as mqtt
import time
import threading   # Para correr el loop MQTT en paralelo con el menú de consola

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

BROKER_MQTT       = "172.18.128.44"
PUERTO_MQTT       = 1883
KEEPALIVE         = 60

TOPICO_CONTROL    = "led/control"   # Para encender/apagar el LED en el ESP32
TOPICO_LUZ        = "sensor/luz"    # Para recibir el nivel de luz del sensor

# Umbral para el modo automático: si la luz es MENOR que este valor,
# se considera que el ambiente está oscuro y el LED se enciende automáticamente
UMBRAL_OSCURIDAD  = 1500

# Estado compartido entre el hilo MQTT y el hilo del menú
estado = {
    "ultimo_luz": None,       # Último valor de la fotoresistencia recibido
    "modo_auto": False,       # True = modo automático activado
}

# ─── CALLBACKS MQTT ───────────────────────────────────────────────────────────

def al_conectar(client, userdata, flags, rc):
    """Suscribirse a sensor/luz al conectarse para recibir retroalimentación."""
    if rc == 0:
        print(f"[MQTT] Conectado a {BROKER_MQTT}")
        client.subscribe(TOPICO_LUZ)
    else:
        print(f"[MQTT ERROR] Código: {rc}")


def al_recibir_mensaje(client, userdata, msg):
    """
    Actualiza el estado local con el último valor de luz recibido.

    En modo automático, este callback también decide si encender o apagar
    el LED basándose en el umbral configurado — lógica de control reactivo.
    """
    if msg.topic == TOPICO_LUZ:
        try:
            valor = int(msg.payload.decode("utf-8").strip())
            estado["ultimo_luz"] = valor

            # Lógica de control automático: actúa solo si el modo está activo
            if estado["modo_auto"]:
                if valor < UMBRAL_OSCURIDAD:
                    client.publish(TOPICO_CONTROL, "1")
                    print(f"\n  [AUTO] Luz baja ({valor}): LED encendido")
                else:
                    client.publish(TOPICO_CONTROL, "0")
                    print(f"\n  [AUTO] Luz suficiente ({valor}): LED apagado")

        except ValueError:
            pass  # Ignorar valores no numéricos silenciosamente


# ─── FUNCIONES DE CONTROL ─────────────────────────────────────────────────────

def encender_led(cliente: mqtt.Client) -> None:
    """Publica '1' en led/control para encender el LED del ESP32."""
    resultado = cliente.publish(TOPICO_CONTROL, "1")
    if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
        print("  [LED] Comando ENCENDER enviado correctamente.")
    else:
        print("  [LED ERROR] No se pudo enviar el comando.")


def apagar_led(cliente: mqtt.Client) -> None:
    """Publica '0' en led/control para apagar el LED del ESP32."""
    resultado = cliente.publish(TOPICO_CONTROL, "0")
    if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
        print("  [LED] Comando APAGAR enviado correctamente.")
    else:
        print("  [LED ERROR] No se pudo enviar el comando.")


def mostrar_estado_actual() -> None:
    """Imprime el último valor de luz recibido y el modo actual."""
    luz = estado["ultimo_luz"]
    modo = "AUTOMÁTICO" if estado["modo_auto"] else "MANUAL"
    if luz is not None:
        print(f"  [ESTADO] Luz actual: {luz}/4095  |  Modo: {modo}")
    else:
        print(f"  [ESTADO] Sin lecturas aún  |  Modo: {modo}")


# ─── MENÚ INTERACTIVO ─────────────────────────────────────────────────────────

def menu_consola(cliente: mqtt.Client) -> None:
    """
    Bucle de menú interactivo en consola.

    Corre en el hilo principal mientras el cliente MQTT opera en un hilo
    de fondo (loop_start). Esto permite publicar comandos mientras se
    siguen recibiendo mensajes de sensor/luz en paralelo.
    """
    print("\n" + "═" * 45)
    print("  CONTROLADOR LED — Menú interactivo")
    print("═" * 45)

    while True:
        print("\n  Opciones:")
        print("    1 → Encender LED")
        print("    0 → Apagar LED")
        print("    a → Activar modo automático (luz baja = LED encendido)")
        print("    m → Desactivar modo automático (volver a manual)")
        print("    s → Ver estado actual del sensor")
        print("    q → Salir")
        print()

        opcion = input("  Ingrese opción: ").strip().lower()

        if opcion == "1":
            estado["modo_auto"] = False  # Modo manual al dar un comando directo
            encender_led(cliente)

        elif opcion == "0":
            estado["modo_auto"] = False
            apagar_led(cliente)

        elif opcion == "a":
            estado["modo_auto"] = True
            print(f"  [MODO AUTO] Activado. Umbral: {UMBRAL_OSCURIDAD}/4095")

        elif opcion == "m":
            estado["modo_auto"] = False
            print("  [MODO MANUAL] Activado.")

        elif opcion == "s":
            mostrar_estado_actual()

        elif opcion == "q":
            print("  Saliendo del controlador...")
            break

        else:
            print("  Opción no reconocida. Use 0, 1, a, m, s o q.")


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  CONTROLADOR LED — pySerial + MQTT")
    print(f"  Control: {TOPICO_CONTROL}  |  Feedback: {TOPICO_LUZ}")
    print("=" * 55)

    cliente = mqtt.Client()
    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje

    try:
        cliente.connect(BROKER_MQTT, PUERTO_MQTT, KEEPALIVE)
    except Exception as e:
        print(f"[FATAL] No se pudo conectar al broker: {e}")
        return

    # loop_start() lanza el cliente MQTT en un hilo de fondo no bloqueante,
    # lo que permite que el menú de consola corra en el hilo principal
    cliente.loop_start()
    time.sleep(1)  # Dar tiempo a que se establezca la conexión

    try:
        menu_consola(cliente)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupción por teclado.")
    finally:
        cliente.loop_stop()
        cliente.disconnect()
        print("[INFO] Controlador desconectado.")


if __name__ == "__main__":
    main()
