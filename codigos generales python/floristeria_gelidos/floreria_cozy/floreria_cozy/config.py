"""
config.py — Configuración centralizada de assets y constantes del juego
========================================================================
Todas las constantes visuales, de gameplay y de assets se definen aquí.
Esto permite cambiar parámetros del juego sin tocar la lógica de módulos.
"""

# ── Dimensiones de la ventana ─────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
TILE_SIZE     = 48   # Tamaño de cada tile en la cuadrícula (píxeles)

# ── Colores (paleta estilo Animal Crossing / cozy) ────────────
# Fondo y tierra
COLOR_GRASS        = (134, 194, 107)
COLOR_GRASS_DARK   = (110, 170,  85)
COLOR_SOIL         = (139,  90,  43)
COLOR_SOIL_LIGHT   = (160, 110,  60)
COLOR_PATH         = (220, 195, 160)
COLOR_PATH_DARK    = (200, 175, 140)

# UI
COLOR_UI_BG        = (255, 248, 230)
COLOR_UI_PANEL     = (250, 235, 210)
COLOR_UI_BORDER    = (180, 140, 100)
COLOR_UI_ACCENT    = (255, 150, 100)
COLOR_UI_TEXT      = ( 80,  50,  30)
COLOR_UI_TEXT_LIGHT= (140, 100,  70)
COLOR_UI_BUTTON    = (255, 200, 120)
COLOR_UI_BTN_HOVER = (255, 220, 150)
COLOR_UI_BTN_PRESS = (230, 170,  90)
COLOR_UI_SUCCESS   = ( 90, 200, 120)
COLOR_UI_DANGER    = (220,  80,  80)
COLOR_UI_GOLD      = (255, 200,  50)
COLOR_UI_SHADOW    = ( 60,  40,  20, 80)

# Flores
FLOWER_COLORS = {
    "rose":      {"petal": (220,  60,  80), "center": (255, 200,  50), "stem": ( 60, 140,  60)},
    "tulip":     {"petal": (255, 120,  60), "center": (255, 240, 100), "stem": ( 70, 150,  70)},
    "sunflower": {"petal": (255, 210,  40), "center": (120,  70,  20), "stem": ( 80, 160,  80)},
    "lavender":  {"petal": (170, 130, 220), "center": (200, 160, 240), "stem": ( 90, 150,  90)},
    "daisy":     {"petal": (255, 255, 230), "center": (255, 220,  60), "stem": ( 70, 140,  60)},
    "orchid":    {"petal": (220, 100, 200), "center": (255, 180, 230), "stem": ( 80, 150,  80)},
}

# Personaje
COLOR_PLAYER_BODY  = (255, 220, 170)  # piel
COLOR_PLAYER_SHIRT = (100, 180, 220)  # camisa azul cielo
COLOR_PLAYER_PANTS = (120,  90, 160)  # pantalón lila
COLOR_PLAYER_HAIR  = (160,  90,  30)

# Clientes (variaciones de color de piel y ropa)
CUSTOMER_PALETTES = [
    {"body": (255, 220, 170), "shirt": (220, 100,  80), "hair": (80,  50, 20)},
    {"body": (220, 170, 120), "shirt": ( 80, 180, 120), "hair": (30,  20, 10)},
    {"body": (160, 110,  70), "shirt": (120, 140, 220), "hair": (20,  15,  5)},
    {"body": (255, 230, 190), "shirt": (200,  80, 160), "hair": (200, 150, 80)},
    {"body": (190, 140, 100), "shirt": (240, 200,  60), "hair": ( 60,  40, 20)},
]

# ── Parámetros de gameplay ────────────────────────────────────
# Economía
STARTING_MONEY         = 500.0
SEED_PRICES = {
    "rose":      12.0,
    "tulip":      8.0,
    "sunflower":  6.0,
    "lavender":  10.0,
    "daisy":      5.0,
    "orchid":    20.0,
}
FLOWER_SELL_PRICES = {  # Precio base de venta al cliente
    "rose":      35.0,
    "tulip":     22.0,
    "sunflower": 18.0,
    "lavender":  28.0,
    "daisy":     14.0,
    "orchid":    55.0,
}

# Tiempo de crecimiento en segundos (reales; se puede acelerar con el factor)
GROWTH_TIME = {
    "rose":      30.0,
    "tulip":     20.0,
    "sunflower": 25.0,
    "lavender":  35.0,
    "daisy":     15.0,
    "orchid":    50.0,
}

# Velocidades y mecánicas
PLAYER_SPEED           = 180.0   # píxeles por segundo
CUSTOMER_SPEED         = 80.0
CUSTOMER_SPAWN_INTERVAL= 18.0    # segundos entre clientes
CUSTOMER_PATIENCE      = 45.0    # segundos antes de irse molesto
CHECKOUT_TIME          = 2.5     # segundos para procesar un cliente en caja

# Día/noche
DAY_DURATION           = 180.0   # segundos por día (3 min = 1 día de juego)
STORE_OPEN_HOUR        = 8       # hora de apertura (0-24)
STORE_CLOSE_HOUR       = 20      # hora de cierre

# Reputación
MAX_REPUTATION         = 100.0
REPUTATION_GAIN_SALE   = 2.0
REPUTATION_LOSS_LEAVE  = 5.0

# ── Layout del mapa ───────────────────────────────────────────
# El mapa es una cuadrícula de tiles.
# 0 = suelo interior, 1 = pared, 2 = jardín/tierra, 3 = camino exterior
# El mapa se define en shop.py para mantener modularidad.

MAP_COLS = 26
MAP_ROWS = 15

# Posiciones clave (col, row) en la cuadrícula
PLAYER_START     = (12, 10)
CASH_REGISTER    = (20,  9)
GARDEN_AREA      = [(c, r) for r in range(2, 6) for c in range(1, 7)]
SHELF_POSITIONS  = [
    (10, 5), (11, 5), (12, 5), (13, 5), (14, 5),
    (10, 7), (11, 7), (12, 7), (13, 7), (14, 7),
    (17, 5), (18, 5), (19, 5),
    (17, 7), (18, 7), (19, 7),
]
DOOR_POSITION    = (12, 13)

# ── Archivos de guardado ──────────────────────────────────────
SAVE_FILE = "saves/savegame.json"
