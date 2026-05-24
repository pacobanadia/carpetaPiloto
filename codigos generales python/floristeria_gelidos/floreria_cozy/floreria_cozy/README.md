# 🌸 Florería Cozy

Un juego de gestión de floristería al estilo Animal Crossing, construido con Python y Pygame.

---

## Requisitos del sistema

- Python 3.10 o superior
- pip

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el juego
python main.py
```

---

## Controles

| Tecla         | Acción                                      |
|---------------|---------------------------------------------|
| W / A / S / D | Mover al personaje                          |
| ↑ ↓ ← →       | Mover al personaje (flechas)                |
| G             | Plantar semilla / Cosechar flor (al lado)   |
| F             | Reabastecer estante cercano                 |
| E             | Cobrar cliente en caja registradora         |
| Click izq.    | Plantar/cosechar/reabastecer con el ratón   |

### Botones del HUD (esquina inferior izquierda)

| Botón       | Panel que abre                              |
|-------------|---------------------------------------------|
| 🌱 Semillas  | Comprar semillas al proveedor               |
| 🌸 Inventario| Ver flores y semillas en tu inventario      |
| 💰 Precios   | Ajustar precios de cada estante             |

---

## Bucle de juego

```
1. Comprar semillas  (panel 🌱)
2. Ir al jardín (área superior izquierda) → plantar [G]
3. Esperar que crezcan las flores
4. Cosechar flores maduras [G]
5. Acercarse a un estante → reabastecer [F]
6. Ajustar precios si lo deseas (panel 💰)
7. Atender a los clientes en la caja [E]
8. Al terminar el día → ver resumen y continuar
```

---

## Estructura del proyecto

```
floreria_cozy/
├── main.py            # Punto de entrada, bucle Pygame
├── game_manager.py    # Director central, coordinación de subsistemas
├── player.py          # Personaje del jugador, movimiento y animaciones
├── customer.py        # IA de clientes, CustomerManager
├── plants.py          # Jardín, macetas, crecimiento de flores
├── shop.py            # Mapa de tiles, estantes, caja registradora
├── inventory.py       # Inventario del jugador y ShelfSlot
├── ui.py              # HUD, paneles, notificaciones
├── config.py          # Constantes globales, colores, precios, layout
├── requirements.txt
├── README.md
└── saves/
    └── savegame.json  # Guardado automático al final de cada día
```

---

## Flores disponibles

| Flor        | Semilla | Precio venta | Tiempo cultivo |
|-------------|---------|--------------|----------------|
| Daisy       | $5      | $14          | 15 s           |
| Tulip       | $8      | $22          | 20 s           |
| Sunflower   | $6      | $18          | 25 s           |
| Rose        | $12     | $35          | 30 s           |
| Lavender    | $10     | $28          | 35 s           |
| Orchid      | $20     | $55          | 50 s           |

> Los tiempos de cultivo son en segundos reales (un día de juego dura 3 minutos).

---

## Guardado automático

La partida se guarda automáticamente en `saves/savegame.json` al final de cada día y al cerrar la ventana.
Para iniciar una partida nueva, elimina ese archivo.

---

## Arquitectura

El juego sigue una arquitectura orientada a objetos con separación clara de responsabilidades:

- **`GameManager`** actúa como director (Facade) y coordina todos los módulos.
- **`Shop`** gestiona el mapa de tiles y los estantes; no conoce a los clientes directamente.
- **`CustomerManager`** controla la IA de clientes mediante una máquina de estados finita.
- **`PlantManager`** actualiza el crecimiento de todas las macetas mediante delta-time.
- **`UI`** es puramente visual; recibe un diccionario de estado y emite acciones al director.
- **`config.py`** centraliza todos los parámetros ajustables del juego.
