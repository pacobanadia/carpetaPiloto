# Ruta 8 — pySerial + MQTT: ESP32 con Fotoresistencia y Control de LED

**Modalidad elegida:** Ruta 8 — Comunicación serial con pySerial e integración con broker MQTT (Mosquitto).

---

## Tutorial y documentación base

Se siguió la documentación oficial de [paho-mqtt](https://eclipse.dev/paho/clients/python/docs/) para la configuración del cliente MQTT en Python, la referencia de [pySerial](https://pyserial.readthedocs.io/) para la lectura del puerto serial, y la guía de instalación de Mosquitto en Linux para levantar el broker en una máquina virtual Ubuntu.

---

## Partes implementadas

Se implementaron tres scripts Python que forman el pipeline completo:

- **`productor.py`** — Lee líneas seriales del ESP32 (`LUZ:<valor>,LED:<estado>`), las valida y publica en los tópicos `sensor/luz` y `sensor/led`. También escucha `led/control` y reenvía comandos al ESP32 por serial.
- **`controlador_led.py`** — Menú interactivo en consola que publica comandos en `led/control` y recibe retroalimentación del sensor de luz en tiempo real.
- **`consumidor.py`** — Suscriptor que recibe ambos tópicos (`sensor/#`) y distribuye cada mensaje a tres procesadores independientes: guardado en CSV, alerta por umbral de luz y resumen estadístico.

Del lado del hardware, se programó un **ESP32** con una fotoresistencia (pin 33) y un LED (pin 26), usando `millis()` para enviar lecturas cada 3 segundos sin bloquear la escucha de comandos seriales.

---

## Modificación propia

La adaptación propia se realizó en dos niveles:

1. **`controlador_led.py`** incorpora un **modo automático**: si el valor de la fotoresistencia cae por debajo de un umbral configurable (por defecto 1500/4095), el LED se enciende automáticamente, simulando un sistema de iluminación reactiva. El menú permite alternar entre modo manual y automático en tiempo de ejecución.
2. **`consumidor.py`** aplica el patrón de **clase abstracta** (`ProcesadorMensaje`) para separar responsabilidades: el consumidor MQTT no contiene lógica de negocio propia, sino que delega cada mensaje a una lista intercambiable de procesadores concretos.

---

## Qué aprendimos

- Cómo establecer comunicación bidireccional entre Python y un microcontrolador mediante pySerial, incluyendo el manejo del reinicio del ESP32 al abrir el puerto.
- La arquitectura publicador/suscriptor de MQTT y el rol del broker como intermediario desacoplado.
- El uso de `loop_start()` para correr el cliente MQTT en un hilo de fondo, permitiendo que el menú de consola opere en paralelo sin bloquear la recepción de mensajes.
- Cómo el uso de `millis()` en el ESP32 permite multitarea cooperativa sin `delay()`.

---

## Dificultad encontrada

Al ejecutar `productor.py` se presentó un error de importación del módulo `serial`:

```
KeyError: '...\env\Lib\site-packages\serial\abc'
```

La causa fue un **conflicto de nombres** entre `pyserial` (el paquete correcto) y el paquete `serial` de PyPI, ambos instalados en el entorno virtual y con la misma carpeta `serial/` en `site-packages`. Python cargaba el paquete incorrecto y fallaba durante la importación. La solución fue desinstalar ambos y reinstalar únicamente `pyserial` y `paho-mqtt`.

---

## Anexo — Video explicativo

> El siguiente video presenta la demostración en funcionamiento del sistema completo: conexión serial del ESP32, publicación de datos al broker MQTT, control del LED desde el menú interactivo y visualización de lecturas en el consumidor.

📹 **[Ver video explicativo](https://youtu.be/j-grUS0jyYI)**
*(Reemplazar `#` con el enlace real al video)*
