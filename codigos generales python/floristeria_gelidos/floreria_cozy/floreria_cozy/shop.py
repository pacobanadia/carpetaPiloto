"""
shop.py — Mapa, tiles y gestión del espacio de la tienda
=========================================================
Define la cuadrícula del mapa, renderiza los tiles, gestiona los
estantes de exhibición y provee las funciones de colisión y búsqueda
de estantes para los clientes.

Clases:
    TileType — Tipos de tile del mapa
    Shop     — Mapa completo de la tienda
"""

import pygame
import math
from config import (
    TILE_SIZE, MAP_COLS, MAP_ROWS,
    COLOR_GRASS, COLOR_GRASS_DARK, COLOR_SOIL, COLOR_SOIL_LIGHT,
    COLOR_PATH, COLOR_PATH_DARK, COLOR_UI_BG, COLOR_UI_BORDER,
    SHELF_POSITIONS, CASH_REGISTER, GARDEN_AREA, DOOR_POSITION,
    FLOWER_COLORS,
)
from inventory import ShelfSlot


class TileType:
    FLOOR    = 0  # Interior de la tienda (madera clara)
    WALL     = 1  # Pared (no transitable)
    SOIL     = 2  # Tierra del jardín
    PATH     = 3  # Camino exterior
    GRASS    = 4  # Césped exterior
    COUNTER  = 5  # Mostrador/mueble decorativo


# ── Mapa principal (26 cols × 15 rows) ───────────────────────
# Leyenda: 0=suelo interior, 1=pared, 2=tierra jardín,
#          3=camino, 4=césped, 5=mostrador
RAW_MAP = [
    #  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
    [  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # 0
    [  4, 2, 2, 2, 2, 2, 2, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4],  # 1
    [  4, 2, 2, 2, 2, 2, 2, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 2
    [  4, 2, 2, 2, 2, 2, 2, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 3
    [  4, 2, 2, 2, 2, 2, 2, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 4
    [  4, 2, 2, 2, 2, 2, 2, 4, 1, 0, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 0, 0, 1, 4, 4, 4],  # 5
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 6
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 5, 5, 5, 5, 5, 0, 0, 5, 5, 5, 0, 0, 1, 4, 4, 4],  # 7
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 8
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1, 4, 4, 4],  # 9
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 10
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 11
    [  4, 4, 4, 4, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4],  # 12
    [  3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3],  # 13
    [  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # 14
]


class Shop:
    """
    Mapa de la tienda con tiles, estantes, caja registradora y
    funciones de soporte para colisión y búsqueda de estantes.
    """

    def __init__(self):
        self.map = [row[:] for row in RAW_MAP]

        # Crear ranuras de estante a partir de las posiciones config
        self.shelves: list[ShelfSlot] = [
            ShelfSlot(col, row) for col, row in SHELF_POSITIONS
        ]

        # Precalcular colores de tile con variación para texturas
        self._floor_surf  = self._make_floor_tile()
        self._wall_surf   = self._make_wall_tile()
        self._soil_surf   = self._make_soil_tile()
        self._path_surf   = self._make_path_tile()
        self._grass_surf  = self._make_grass_tile()
        self._counter_surf= self._make_counter_tile()

        # Decoraciones
        self._decorations = self._place_decorations()

        # Fila de caja (lista de clientes esperando; gestionada por CustomerManager)
        self._queue: list = []

    # ── Tiles ─────────────────────────────────────────────────

    def _make_floor_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((230, 210, 180))
        # Líneas de duela
        for i in range(0, TILE_SIZE, 12):
            pygame.draw.line(s, (210, 190, 160), (0, i), (TILE_SIZE, i), 1)
        pygame.draw.rect(s, (200, 180, 150), s.get_rect(), 1)
        return s

    def _make_wall_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((170, 130, 90))
        # Textura de ladrillo
        for row in range(0, TILE_SIZE, 10):
            offset = 12 if (row // 10) % 2 else 0
            for col in range(-offset, TILE_SIZE + 24, 24):
                pygame.draw.rect(s, (150, 110, 70), (col, row, 22, 8))
                pygame.draw.rect(s, (130, 95, 60), (col, row, 22, 8), 1)
        return s

    def _make_soil_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill(COLOR_SOIL)
        import random
        rng = random.Random(42)
        for _ in range(8):
            x = rng.randint(2, TILE_SIZE - 4)
            y = rng.randint(2, TILE_SIZE - 4)
            pygame.draw.ellipse(s, COLOR_SOIL_LIGHT, (x, y, 4, 3))
        pygame.draw.rect(s, (110, 70, 30), s.get_rect(), 1)
        return s

    def _make_path_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill(COLOR_PATH)
        pygame.draw.rect(s, COLOR_PATH_DARK, s.get_rect(), 1)
        import random
        rng = random.Random(7)
        for _ in range(5):
            x = rng.randint(3, TILE_SIZE - 6)
            y = rng.randint(3, TILE_SIZE - 6)
            pygame.draw.ellipse(s, COLOR_PATH_DARK, (x, y, 5, 3))
        return s

    def _make_grass_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill(COLOR_GRASS)
        import random
        rng = random.Random(99)
        for _ in range(6):
            x = rng.randint(0, TILE_SIZE - 4)
            y = rng.randint(0, TILE_SIZE - 4)
            pygame.draw.ellipse(s, COLOR_GRASS_DARK, (x, y, 4, 3))
        return s

    def _make_counter_tile(self):
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        s.fill((180, 130, 80))
        pygame.draw.rect(s, (140, 100, 55), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4))
        pygame.draw.rect(s, (120, 85, 45), s.get_rect(), 2)
        return s

    # ── Decoraciones ──────────────────────────────────────────

    def _place_decorations(self) -> list[dict]:
        """Lista de objetos decorativos con posición y tipo."""
        return [
            {"type": "pot",    "col":  8, "row": 3},
            {"type": "pot",    "col":  8, "row": 5},
            {"type": "banner", "col": 15, "row": 2},
            {"type": "sign",   "col": 12, "row": 13},
        ]

    def _draw_decoration(self, surface, dec: dict, cam_x: int, cam_y: int):
        col, row = dec["col"], dec["row"]
        sx = col * TILE_SIZE - cam_x
        sy = row * TILE_SIZE - cam_y
        cx = sx + TILE_SIZE // 2
        cy = sy + TILE_SIZE // 2

        if dec["type"] == "pot":
            pygame.draw.polygon(surface, (180, 100, 60),
                                [(cx - 8, cy + 8), (cx + 8, cy + 8),
                                 (cx + 6, cy - 4), (cx - 6, cy - 4)])
            pygame.draw.rect(surface, (150, 80, 40), (cx - 8, cy + 6, 16, 4))
            pygame.draw.ellipse(surface, (80, 160, 80), (cx - 4, cy - 10, 8, 14))

        elif dec["type"] == "banner":
            for i, color in enumerate([(220, 100, 100), (100, 180, 220),
                                        (220, 200, 80), (160, 200, 100)]):
                pygame.draw.polygon(surface, color,
                                    [(cx + i * 14 - 28, cy),
                                     (cx + i * 14 - 21, cy),
                                     (cx + i * 14 - 24, cy + 10)])

        elif dec["type"] == "sign":
            pygame.draw.rect(surface, (180, 130, 70), (cx - 20, cy - 10, 40, 20),
                             border_radius=4)
            pygame.draw.rect(surface, (140, 100, 50), (cx - 20, cy - 10, 40, 20),
                             border_radius=4, width=2)

    # ── Colisión ──────────────────────────────────────────────

    def is_walkable(self, px: float, py: float) -> bool:
        """True si la posición en píxeles es transitable."""
        margin = 12
        col = int(px // TILE_SIZE)
        row = int(py // TILE_SIZE)
        if not (0 <= col < MAP_COLS and 0 <= row < MAP_ROWS):
            return False
        tile = self.map[row][col]
        return tile not in (TileType.WALL, TileType.COUNTER)

    # ── Estantes ──────────────────────────────────────────────

    def get_shelf_at(self, col: int, row: int) -> ShelfSlot | None:
        for shelf in self.shelves:
            if shelf.col == col and shelf.row == row:
                return shelf
        return None

    def find_shelf_for_customer(self, customer) -> ShelfSlot | None:
        """
        Busca un estante disponible (con stock) compatible con las
        preferencias del cliente. Evita estantes ya asignados.
        """
        available = [
            s for s in self.shelves
            if not s.is_empty and s != customer.assigned_shelf
            and all(c.assigned_shelf != s
                    for c in getattr(self, '_customer_list', [])
                    if c != customer)
        ]
        if not available:
            return None

        # Filtrar por preferencia de flor si tiene una
        if customer.desired_flower:
            preferred = [s for s in available if s.flower_type == customer.desired_flower]
            if preferred:
                available = preferred

        import random
        return random.choice(available)

    def get_queue_position(self, customer) -> int:
        """Asigna posición en la fila."""
        return len(self._queue)

    # ── Caja registradora ─────────────────────────────────────

    def is_near_cash_register(self, player_col: int, player_row: int) -> bool:
        return (abs(player_col - CASH_REGISTER[0]) <= 2 and
                abs(player_row - CASH_REGISTER[1]) <= 2)

    # ── Renderizado ───────────────────────────────────────────

    def draw(self, surface, camera_x: int, camera_y: int,
             time_elapsed: float = 0.0):
        """Dibuja todos los tiles visibles en pantalla."""
        import pygame
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Rango de tiles a dibujar (frustum culling simple)
        col_start = max(0, camera_x // TILE_SIZE)
        col_end   = min(MAP_COLS, col_start + screen_w // TILE_SIZE + 2)
        row_start = max(0, camera_y // TILE_SIZE)
        row_end   = min(MAP_ROWS, row_start + screen_h // TILE_SIZE + 2)

        tile_map = {
            TileType.FLOOR:   self._floor_surf,
            TileType.WALL:    self._wall_surf,
            TileType.SOIL:    self._soil_surf,
            TileType.PATH:    self._path_surf,
            TileType.GRASS:   self._grass_surf,
            TileType.COUNTER: self._counter_surf,
        }

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                tile_type = self.map[row][col]
                tile_surf = tile_map.get(tile_type, self._floor_surf)
                sx = col * TILE_SIZE - camera_x
                sy = row * TILE_SIZE - camera_y
                surface.blit(tile_surf, (sx, sy))

        # Dibujar estantes con su contenido
        for shelf in self.shelves:
            self._draw_shelf(surface, shelf, camera_x, camera_y, time_elapsed)

        # Caja registradora
        self._draw_cash_register(surface, camera_x, camera_y)

        # Puerta
        self._draw_door(surface, camera_x, camera_y)

        # Decoraciones
        for dec in self._decorations:
            self._draw_decoration(surface, dec, camera_x, camera_y)

    def _draw_shelf(self, surface, shelf: ShelfSlot,
                    cam_x: int, cam_y: int, time_elapsed: float):
        """Dibuja una ranura de estante con las flores que contiene."""
        sx = shelf.col * TILE_SIZE - cam_x
        sy = shelf.row * TILE_SIZE - cam_y

        # Base del estante
        pygame.draw.rect(surface, (160, 115, 65),
                         (sx + 2, sy + 4, TILE_SIZE - 4, TILE_SIZE - 8),
                         border_radius=4)
        pygame.draw.rect(surface, (130, 90, 45),
                         (sx + 2, sy + 4, TILE_SIZE - 4, TILE_SIZE - 8),
                         border_radius=4, width=2)

        # Flores en el estante
        if shelf.flower_type and shelf.stock > 0:
            colors = FLOWER_COLORS.get(shelf.flower_type, FLOWER_COLORS["daisy"])
            cx = sx + TILE_SIZE // 2
            cy = sy + TILE_SIZE // 2 - 4
            # Pequeñas flores decorativas
            for i in range(min(shelf.stock, 5)):
                ox = (i - 2) * 7
                sway = math.sin(time_elapsed * 1.2 + i * 1.1) * 1.5
                # Tallo
                pygame.draw.line(surface, colors["stem"],
                                 (cx + ox + int(sway), cy + 8),
                                 (cx + ox + int(sway), cy), 2)
                # Cabeza de flor pequeña
                for j in range(6):
                    angle = math.radians(j * 60 + time_elapsed * 10)
                    px = cx + ox + int(sway) + int(math.cos(angle) * 4)
                    py = cy + int(math.sin(angle) * 4)
                    pygame.draw.circle(surface, colors["petal"], (px, py), 2)
                pygame.draw.circle(surface, colors["center"],
                                   (cx + ox + int(sway), cy), 2)

            # Precio
            font = pygame.font.SysFont("segoeui", 11, bold=True)
            price_str = f"${shelf.price:.0f}"
            txt = font.render(price_str, True, (60, 40, 10))
            surface.blit(txt, (sx + TILE_SIZE // 2 - txt.get_width() // 2,
                                sy + TILE_SIZE - 14))
        else:
            # Estante vacío
            font = pygame.font.SysFont("segoeui", 10)
            txt = font.render("vacío", True, (160, 130, 100))
            surface.blit(txt, (sx + TILE_SIZE // 2 - txt.get_width() // 2,
                                sy + TILE_SIZE // 2 - 6))

    def _draw_cash_register(self, surface, cam_x: int, cam_y: int):
        """Dibuja la caja registradora."""
        col, row = CASH_REGISTER
        sx = col * TILE_SIZE - cam_x
        sy = row * TILE_SIZE - cam_y

        # Base
        pygame.draw.rect(surface, (80, 60, 40),
                         (sx + 2, sy + 4, TILE_SIZE - 4, TILE_SIZE - 6),
                         border_radius=5)
        # Pantalla
        pygame.draw.rect(surface, (100, 200, 140),
                         (sx + 6, sy + 7, TILE_SIZE - 12, 14),
                         border_radius=3)
        # Teclas
        for i in range(3):
            for j in range(2):
                pygame.draw.rect(surface, (60, 45, 30),
                                 (sx + 8 + j * 12, sy + 26 + i * 6, 8, 4),
                                 border_radius=2)
        # Letrero $
        font = pygame.font.SysFont("segoeui", 16, bold=True)
        txt = font.render("$", True, (255, 220, 50))
        surface.blit(txt, (sx + TILE_SIZE // 2 - 4, sy))

    def _draw_door(self, surface, cam_x: int, cam_y: int):
        """Dibuja la puerta de entrada."""
        col, row = DOOR_POSITION
        sx = col * TILE_SIZE - cam_x
        sy = row * TILE_SIZE - cam_y
        # Marco
        pygame.draw.rect(surface, (140, 100, 60),
                         (sx, sy, TILE_SIZE * 2, TILE_SIZE * 2 // 3),
                         border_radius=4)
        pygame.draw.rect(surface, (180, 140, 90),
                         (sx + 2, sy + 2, TILE_SIZE * 2 - 4, TILE_SIZE * 2 // 3 - 4),
                         border_radius=3)
        # Manija
        pygame.draw.circle(surface, (200, 160, 50), (sx + TILE_SIZE + 8, sy + 16), 3)

    def to_dict(self) -> list:
        return [s.to_dict() for s in self.shelves]

    def from_dict(self, data: list):
        for sdata in data:
            shelf = self.get_shelf_at(sdata["col"], sdata["row"])
            if shelf:
                shelf.from_dict(sdata)
