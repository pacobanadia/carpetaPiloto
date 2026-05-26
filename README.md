# Ruta 8 — pySerial + MQTT ·  IoT con ESP32

**Nombre del estudiante:** Daniel Cano Duque  
**Modalidad:** Individual  
**Fecha de entrega:** 27 Mayo 2026

---

## Modalidad elegida

**Ruta 8 — pySerial + MQTT, Opción A:** ESP32 conectado por USB serial a un PC,
con Python como puente hacia un broker MQTT propio en linux.

---

## Documentación y tutoriales seguidos

- pySerial — Short Introduction: [https://pyserial.readthedocs.io/en/latest/shortintro.html](https://pyserial.readthedocs.io/en/latest/tools.html)
- Eclipse Paho MQTT mosquitto.conf: [(https://mosquitto.org/man/mosquitto-conf-5.html)](https://mosquitto.org/man/mosquitto-conf-5.html)
- Alswnet. (s. f.). NocheProgramacion/series/mqtt at master · alswnet/NocheProgramacion. GitHub. https://github.com/alswnet/NocheProgramacion/tree/master/series/mqtt
- ChepeCarlos. (2021, 30 julio). 💻 Aprende a usar Mosquitto_Sub y Mosquitto_Pub para conectar a MQTT [Vídeo]. YouTube. https://www.youtube.com/watch?v=O10JqPeC5SA
---

## Partes implementadas

| Archivo                  | Rol en el pipeline                                              |
|--------------------------|-----------------------------------------------------------------|
| `esp32_sensor.ino`       | Firmware del ESP32: lee la fotoresistencia y controla el LED   |
| `scripts/productor.py`   | Lee el puerto serial y publica en `sensor/luz` y `sensor/led` |
| `scripts/consumidor.py`  | Se suscribe a ambos tópicos, registra en CSV y genera alertas  |
| `scripts/controlador_led.py` | Menú interactivo para controlar el LED + modo automático   |

**Pipeline completo:**

```
ESP32 (LDR + LED)
  │ USB Serial "LUZ:xxxx,LED:x\n"
  ▼
productor.py  (pySerial → parseo → validación)
  │ MQTT publish → sensor/luz  /  sensor/led
  ▼
broker.hivemq.com:1883
  │ MQTT subscribe sensor/#
  ▼
consumidor.py  →  data/lecturas.csv  +  alertas en consola
```

---

## Modificación propia

El archivo `controlador_led.py` es la adaptación propia. Combina **publicación y suscripción en un mismo cliente** con un **menú interactivo en consola** y un **modo automático**: el LED se enciende solo cuando el valor del sensor de luz cae por debajo de un umbral configurable (`UMBRAL_OSCURIDAD = 1500`). Esto simula un sistema de iluminación.

Adicionalmente, el `consumidor.py` genera **resúmenes estadísticos periódicos** (promedio, mínimo, máximo) y una **barra de nivel visual** en consola, también como adaptación propia.

---

## Qué aprendimos

- La diferencia entre `loop_forever()` (bloqueante) y `loop_start()` (hilo de fondo),
  y cuándo usar cada uno.
- Que el ESP32 reinicia al abrirse el puerto serial, por lo que `time.sleep(2)` en
  `conectar_serial()` es imprescindible para no leer datos corruptos del arranque.
- Cómo manejar errores de serial sin detener el programa (`SerialException` en un
  `try/except` dentro del bucle de lectura).
- La importancia de definir un formato de mensaje claro y consistente desde el firmware
  (`"LUZ:<n>,LED:<m>\n"`) antes de escribir el código Python.

## Dificultades encontradas

- Identificar el puerto COM correcto en Windows requirió abrir el Administrador de
  dispositivos; en Linux habría sido `/dev/ttyUSB0`.
- El broker público HiveMQ no garantiza entrega exclusiva: si otros proyectos usaban
  los mismos tópicos genéricos, llegaban mensajes ajenos. Se resolvió usando tópicos
  con un prefijo más específico (`sensor/luz` en lugar de `luz`).
