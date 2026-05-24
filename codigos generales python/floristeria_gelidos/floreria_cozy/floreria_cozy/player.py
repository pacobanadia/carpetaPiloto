"""
player.py — Módulo del personaje del jugador
=============================================
Gestiona la posición, movimiento, animaciones de caminar y
todas las interacciones del jugador con el mundo del juego:
recoger flores, reabastecer estantes, cobrar en caja.

Clase principal:
    Player — Personaje controlado por el jugador
"""

import pygame
import math
from config import (
    PLAYER_SPEED, TILE_SIZE,
    COLOR_PLAYER_BODY, COLOR_PLAYER_SHIRT,
    COLOR_PLAYER_PANTS, COLOR_PLAYER_HAIR,
)

# Estados de acción del jugador
class PlayerState:
    IDLE     = "idle"
    WALKING  = "walking"
    PLANTING = "planting"
    HARVEST  = "harvesting"
    STOCKING = "stocking"
    CHECKOUT = "checkout"


class Player:
    """
    Personaje del jugador con movimiento suave (top-down), animaciones
    de caminar mediante oscilación de extremidades y lógica de interacción.
    """

    SIZE = 20  # Radio de colisión aproximado

    def __init__(self, start_col: int, start_row: int):
        # Posición en píxeles (centro del sprite)
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + TILE_SIZE // 2

        self.state  = PlayerState.IDLE
        self.facing = "down"    # Dirección: up / down / left / right

        # Animación de caminar
        self._walk_cycle  = 0.0   # 0..2π ciclo de piernas
        self._action_timer= 0.0   # Temporizador para acciones (plantar, cobrar…)
        self._action_callback = None  # Función llamada al completar la acción

        # Indicador visual de interacción (flotar texto sobre el personaje)
        self._interaction_text = ""
        self._interaction_timer = 0.0

    # ── Movimiento ────────────────────────────────────────────

    def handle_input(self, keys, dt: float, collision_fn):
        """
        Procesa WASD/flechas para mover el personaje.
        collision_fn(x, y) → True si la posición es transitable.
        """
        if self.state in (PlayerState.PLANTING, PlayerState.HARVEST,
                          PlayerState.STOCKING, PlayerState.CHECKOUT):
            return  # Bloqueado durante acciones

        dx = dy = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1

        # Normalizar diagonal
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
            self.state = PlayerState.WALKING
            # Actualizar dirección de cara
            if abs(dx) > abs(dy):
                self.facing = "right" if dx > 0 else "left"
            else:
                self.facing = "down" if dy > 0 else "up"
        else:
            self.state = PlayerState.IDLE

        # Mover en X
        nx = self.x + dx * PLAYER_SPEED * dt
        if collision_fn(nx, self.y):
            self.x = nx

        # Mover en Y
        ny = self.y + dy * PLAYER_SPEED * dt
        if collision_fn(self.x, ny):
            self.y = ny

    def update(self, dt: float):
        """Actualiza temporizadores de animación y acciones en progreso."""
        # Ciclo de caminar
        if self.state == PlayerState.WALKING:
            self._walk_cycle += dt * 8.0
        else:
            # Volver suavemente a posición neutral
            self._walk_cycle *= 0.85

        # Acción en progreso
        if self._action_timer > 0:
            self._action_timer -= dt
            if self._action_timer <= 0:
                self._action_timer = 0
                if self._action_callback:
                    self._action_callback()
                    self._action_callback = None
                self.state = PlayerState.IDLE

        # Texto flotante
        if self._interaction_timer > 0:
            self._interaction_timer -= dt

    # ── Acciones ──────────────────────────────────────────────

    def start_action(self, state: str, duration: float, callback=None,
                     text: str = ""):
        """Inicia una acción temporizada (plantar, cosechar, cobrar…)."""
        self.state           = state
        self._action_timer   = duration
        self._action_callback= callback
        if text:
            self.show_text(text)

    def show_text(self, text: str, duration: float = 1.5):
        """Muestra texto flotante sobre el personaje."""
        self._interaction_text  = text
        self._interaction_timer = duration

    # ── Posición en cuadrícula ────────────────────────────────

    @property
    def col(self) -> int:
        return int(self.x // TILE_SIZE)

    @property
    def row(self) -> int:
        return int(self.y // TILE_SIZE)

    def distance_to(self, col: int, row: int) -> float:
        tx = col * TILE_SIZE + TILE_SIZE // 2
        ty = row * TILE_SIZE + TILE_SIZE // 2
        return math.hypot(self.x - tx, self.y - ty)

    # ── Dibujo ────────────────────────────────────────────────

    def draw(self, surface, camera_x: int, camera_y: int):
        """Dibuja el personaje con animación de caminar."""
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Oscilación de piernas
        leg_swing = math.sin(self._walk_cycle) * 5

        # ── Sombra ─────────────────────────────────
        shadow_surf = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 28, 10))
        surface.blit(shadow_surf, (sx - 14, sy + 8))

        # ── Pierna izquierda ────────────────────────
        pygame.draw.rect(surface, COLOR_PLAYER_PANTS,
                         (sx - 6, sy + 4 - int(leg_swing), 5, 10))
        # ── Pierna derecha ──────────────────────────
        pygame.draw.rect(surface, COLOR_PLAYER_PANTS,
                         (sx + 1, sy + 4 + int(leg_swing), 5, 10))

        # ── Cuerpo (camisa) ─────────────────────────
        pygame.draw.rect(surface, COLOR_PLAYER_SHIRT,
                         (sx - 8, sy - 8, 16, 14), border_radius=4)

        # ── Brazos ──────────────────────────────────
        arm_swing = math.sin(self._walk_cycle) * 4
        pygame.draw.rect(surface, COLOR_PLAYER_SHIRT,
                         (sx - 13, sy - 6 + int(arm_swing), 5, 9), border_radius=2)
        pygame.draw.rect(surface, COLOR_PLAYER_SHIRT,
                         (sx + 8, sy - 6 - int(arm_swing), 5, 9), border_radius=2)

        # Manos
        pygame.draw.circle(surface, COLOR_PLAYER_BODY, (sx - 10, sy + 3 + int(arm_swing)), 3)
        pygame.draw.circle(surface, COLOR_PLAYER_BODY, (sx + 10, sy + 3 - int(arm_swing)), 3)

        # ── Cabeza ──────────────────────────────────
        pygame.draw.circle(surface, COLOR_PLAYER_BODY, (sx, sy - 14), 10)

        # ── Cabello ─────────────────────────────────
        pygame.draw.arc(surface, COLOR_PLAYER_HAIR,
                        (sx - 10, sy - 24, 20, 18), 0, math.pi, 5)

        # ── Ojos ────────────────────────────────────
        if self.facing != "up":
            pygame.draw.circle(surface, (60, 40, 20), (sx - 3, sy - 15), 2)
            pygame.draw.circle(surface, (60, 40, 20), (sx + 3, sy - 15), 2)
            # Mejillas
            pygame.draw.circle(surface, (255, 180, 160), (sx - 6, sy - 13), 2)
            pygame.draw.circle(surface, (255, 180, 160), (sx + 6, sy - 13), 2)

        # ── Texto flotante ───────────────────────────
        if self._interaction_timer > 0 and self._interaction_text:
            alpha = min(255, int(self._interaction_timer / 1.5 * 255))
            font = pygame.font.SysFont("segoeui", 14, bold=True)
            text_surf = font.render(self._interaction_text, True, (80, 40, 10))
            text_surf.set_alpha(alpha)
            surface.blit(text_surf,
                         (sx - text_surf.get_width() // 2, sy - 38))

        # ── Indicador de acción ──────────────────────
        if self._action_timer > 0:
            # Barra de progreso circular pequeña
            progress = 1.0 - (self._action_timer / max(self._action_timer + 0.001,
                                                        self._get_action_max()))
            _draw_progress_arc(surface, sx, sy - 32, 10, progress)

    def _get_action_max(self):
        # Solo para calcular progreso visual; se puede afinar
        return 3.0

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

    def from_dict(self, data: dict):
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)


def _draw_progress_arc(surface, cx, cy, r, progress):
    """Dibuja un arco de progreso alrededor del personaje."""
    import math
    if progress <= 0:
        return
    rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
    end_angle = -math.pi / 2 + progress * 2 * math.pi
    try:
        pygame.draw.arc(surface, (255, 200, 50), rect,
                        -math.pi / 2, end_angle, 3)
    except Exception:
        pass
