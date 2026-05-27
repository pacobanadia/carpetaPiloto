"""
consumidor.py — Suscriptor MQTT con clase abstracta ProcesadorMensaje
=====================================================================
Ruta 8. pySerial + MQTT — Opción A

Mejora arquitectónica: se introduce la clase abstracta ProcesadorMensaje
para separar responsabilidades y permitir agregar o quitar comportamientos
sin tocar el núcleo del consumidor MQTT.
"""

import paho.mqtt.client as mqtt
import csv
import os
from abc import ABC, abstractmethod   # ← necesario para la clase abstracta
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

BROKER_MQTT      = "172.18.128.44"
PUERTO_MQTT      = 1883
KEEPALIVE        = 60
TOPICO_LUZ       = "sensor/luz"
TOPICO_LED       = "sensor/led"
TOPICO_TODOS     = "sensor/#"
ARCHIVO_CSV      = "data/lecturas.csv"
UMBRAL_LUZ_ALTA  = 3000
INTERVALO_RESUMEN = 10


# ══════════════════════════════════════════════════════════════════════════════
#  CLASE ABSTRACTA — define el contrato que todo procesador debe cumplir
# ══════════════════════════════════════════════════════════════════════════════

class ProcesadorMensaje(ABC):
    """
    Contrato base para cualquier procesador de mensajes MQTT.

    Toda clase que herede de ProcesadorMensaje DEBE implementar:
      - procesar(topico, valor) : lógica principal al recibir un mensaje
      - nombre                  : propiedad descriptiva (para logs y depuración)

    Al ser abstracta, no puede instanciarse directamente; obliga a que cada
    subclase defina su propio comportamiento concreto.
    """

    @abstractmethod
    def procesar(self, topico: str, valor: str) -> None:
        """
        Ejecuta la acción correspondiente al recibir un mensaje MQTT.

        Parámetros
        ----------
        topico : tópico MQTT donde llegó el mensaje (ej. 'sensor/luz')
        valor  : payload del mensaje ya decodificado como string
        """
        ...

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre descriptivo del procesador (para logs)."""
        ...


# ══════════════════════════════════════════════════════════════════════════════
#  IMPLEMENTACIONES CONCRETAS
# ══════════════════════════════════════════════════════════════════════════════

class RegistradorCSV(ProcesadorMensaje):
    """
    Procesador concreto #1 — Guarda cada mensaje en un archivo CSV.

    Implementa 'procesar' escribiendo una fila con timestamp, tópico,
    valor y unidad en el archivo indicado al construir la instancia.
    """

    def __init__(self, ruta: str):
        self._ruta = ruta
        self._inicializar_csv()

    @property
    def nombre(self) -> str:
        return "RegistradorCSV"

    def _inicializar_csv(self) -> None:
        os.makedirs(os.path.dirname(self._ruta), exist_ok=True)
        if not os.path.exists(self._ruta):
            with open(self._ruta, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp", "topico", "valor", "unidad"])
            print(f"[{self.nombre}] Archivo creado: {self._ruta}")
        else:
            print(f"[{self.nombre}] Agregando a archivo existente: {self._ruta}")

    def procesar(self, topico: str, valor: str) -> None:
        unidades = {TOPICO_LUZ: "ADC_12bit", TOPICO_LED: "boolean"}
        unidad    = unidades.get(topico, "desconocida")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self._ruta, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([timestamp, topico, valor, unidad])
        except IOError as e:
            print(f"[{self.nombre}] ERROR al escribir: {e}")


class AlertaLuz(ProcesadorMensaje):
    """
    Procesador concreto #2 — Emite alertas si la luz supera un umbral.

    Solo actúa sobre el tópico 'sensor/luz'; ignora cualquier otro.
    El umbral se configura en el constructor, lo que hace esta clase
    reutilizable sin cambiar el código fuente.
    """

    def __init__(self, umbral: int = UMBRAL_LUZ_ALTA):
        self._umbral = umbral

    @property
    def nombre(self) -> str:
        return "AlertaLuz"

    def procesar(self, topico: str, valor: str) -> None:
        if topico != TOPICO_LUZ:
            return   # Este procesador solo le interesa el sensor de luz
        try:
            valor_int = int(valor)
        except ValueError:
            return

        if valor_int > self._umbral:
            print(f"  ⚠  [{self.nombre}] Luz alta: {valor_int} > {self._umbral}")


class ResumenEstadisticas(ProcesadorMensaje):
    """
    Procesador concreto #3 — Acumula lecturas e imprime estadísticas periódicas.

    Guarda internamente el historial de valores de luz y, cada
    'intervalo' mensajes de luz, imprime promedio, mínimo y máximo.
    """

    def __init__(self, intervalo: int = INTERVALO_RESUMEN):
        self._intervalo  = intervalo
        self._lecturas   = []
        self._contador   = 0

    @property
    def nombre(self) -> str:
        return "ResumenEstadisticas"

    def procesar(self, topico: str, valor: str) -> None:
        if topico != TOPICO_LUZ:
            return
        try:
            valor_int = int(valor)
        except ValueError:
            return

        self._lecturas.append(valor_int)
        self._contador += 1

        # Barra visual proporcional a 4095
        porcentaje = valor_int / 4095 * 100
        barra = "█" * int(porcentaje / 5) + "░" * (20 - int(porcentaje / 5))
        print(f"[{topico}] {valor_int:4d}/4095  [{barra}]  {porcentaje:.1f}%")

        if self._contador % self._intervalo == 0:
            self._imprimir_resumen()

    def _imprimir_resumen(self) -> None:
        if not self._lecturas:
            return
        print("\n" + "─" * 45)
        print(f"  RESUMEN — últimas {len(self._lecturas)} lecturas de luz")
        print(f"  Promedio : {sum(self._lecturas) / len(self._lecturas):.1f}")
        print(f"  Mínimo   : {min(self._lecturas)}")
        print(f"  Máximo   : {max(self._lecturas)}")
        print("─" * 45 + "\n")
        self._lecturas.clear()


# ══════════════════════════════════════════════════════════════════════════════
#  CONSUMIDOR MQTT — orquesta los procesadores sin conocer su lógica interna
# ══════════════════════════════════════════════════════════════════════════════

class ConsumidorMQTT:
    """
    Gestiona la conexión MQTT y delega cada mensaje a la lista de procesadores.

    Al recibir un mensaje llama a procesador.procesar() por cada elemento
    de self._procesadores. No contiene lógica de negocio propia: eso es
    responsabilidad exclusiva de cada ProcesadorMensaje.
    """

    def __init__(self, broker: str, puerto: int, topico: str,
                 procesadores: list[ProcesadorMensaje]):
        self._broker      = broker
        self._puerto      = puerto
        self._topico      = topico
        self._procesadores = procesadores          # lista de ProcesadorMensaje
        self._cliente     = mqtt.Client()
        self._cliente.on_connect = self._al_conectar
        self._cliente.on_message = self._al_recibir_mensaje

    def _al_conectar(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            print(f"[MQTT] Conectado a {self._broker}:{self._puerto}")
            client.subscribe(self._topico)
            print(f"[MQTT] Suscrito a: {self._topico}")
        else:
            print(f"[MQTT ERROR] Código: {rc}")

    def _al_recibir_mensaje(self, client, userdata, msg) -> None:
        try:
            valor = msg.payload.decode("utf-8").strip()
        except UnicodeDecodeError:
            print(f"[ERROR] Payload no decodificable en {msg.topic}")
            return

        # ← El consumidor simplemente itera y delega; no sabe qué hace cada uno
        for procesador in self._procesadores:
            procesador.procesar(msg.topic, valor)

    def iniciar(self) -> None:
        try:
            self._cliente.connect(self._broker, self._puerto, KEEPALIVE)
        except Exception as e:
            print(f"[FATAL] No se pudo conectar: {e}")
            return

        print("\n[INFO] Escuchando mensajes. Presione Ctrl+C para detener.\n")
        try:
            self._cliente.loop_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Detenido por el usuario.")
        finally:
            self._cliente.disconnect()
            print("[INFO] Consumidor desconectado.")


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  CONSUMIDOR IoT — MQTT + Clase Abstracta")
    print(f"  Tópico : {TOPICO_TODOS}")
    print(f"  CSV    : {ARCHIVO_CSV}")
    print("=" * 55)

    # Construir la lista de procesadores — agregar o quitar sin tocar nada más
    procesadores: list[ProcesadorMensaje] = [
        RegistradorCSV(ARCHIVO_CSV),
        AlertaLuz(umbral=UMBRAL_LUZ_ALTA),
        ResumenEstadisticas(intervalo=INTERVALO_RESUMEN),
    ]

    consumidor = ConsumidorMQTT(
        broker      = BROKER_MQTT,
        puerto      = PUERTO_MQTT,
        topico      = TOPICO_TODOS,
        procesadores = procesadores,
    )
    consumidor.iniciar()


if __name__ == "__main__":
    main()