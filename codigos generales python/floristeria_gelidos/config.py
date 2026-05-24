import pygame

# Configuración global del juego
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colores cozy (Animal Crossing style)
COLORS = {
    'bg_day': (135, 206, 235),
    'bg_night': (25, 25, 51),
    'grass': (34, 139, 34),
    'wood': (139, 69, 19),
    'ui_bg': (255, 248, 220),
    'ui_border': (160, 82, 45),
    'text': (51, 25, 0),
    'success': (144, 238, 144),
    'warning': (255, 218, 185),
}

# Posiciones fijas
SHOP_AREA = pygame.Rect(200, 100, 880, 500)
GARDEN_AREA = pygame.Rect(50, 400, 300, 250)
UI_PANEL = pygame.Rect(10, 10, 300, 700)

# Datos de flores
FLOWER_DATA = {
    'rosa': {'growth_time': 300, 'price': 5, 'color': (255, 20, 147)},
    'margarita': {'growth_time': 200, 'price': 3, 'color': (255, 255, 255)},
    'tulpan': {'growth_time': 250, 'price': 4, 'color': (255, 105, 180)},
    'girasol': {'growth_time': 400, 'price': 8, 'color': (255, 215, 0)},
}