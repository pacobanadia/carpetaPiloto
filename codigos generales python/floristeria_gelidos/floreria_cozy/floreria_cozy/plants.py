"""
plants.py — Sistema de jardín y cultivo de flores
==================================================
Gestiona las macetas del jardín trasero: plantado, crecimiento
por etapas y cosecha. El crecimiento es en tiempo real (dt).

Clases:
    PlantStage  — Enumeración de etapas de crecimiento
    Plant       — Una maceta individual con su flor
    PlantManager— Gestiona todas las macetas del jardín
"""

from enum import IntEnum
import math
from config import GROWTH_TIME, GARDEN_AREA, TILE_SIZE, FLOWER_COLORS


class PlantStage(IntEnum):
    EMPTY    = 0   # Sin semilla
    SEED     = 1   # Semilla plantada, invisible
    SPROUT   = 2   # Brote pequeño
    GROWING  = 3   # Planta en desarrollo
    READY    = 4   # Lista para cosechar


class Plant:
    """
    Representa una maceta individual en el jardín.
    El progreso de crecimiento va de 0.0 a 1.0.
    """

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.flower_type: str | None = None
        self.stage = PlantStage.EMPTY
        self.growth_progress: float = 0.0   # 0.0 = recién plantada, 1.0 = lista
        self._growth_time: float = 0.0       # duración total de crecimiento

        # Animación: oscilación suave de la planta
        self._anim_offset: float = (col * 7 + row * 13) % (2 * math.pi)

    def plant_seed(self, flower_type: str) -> bool:
        """Planta una semilla si la maceta está vacía."""
        if self.stage != PlantStage.EMPTY:
            return False
        self.flower_type = flower_type
        self.stage = PlantStage.SEED
        self.growth_progress = 0.0
        self._growth_time = GROWTH_TIME.get(flower_type, 30.0)
        return True

    def update(self, dt: float, time_elapsed: float):
        """Avanza el crecimiento en función del tiempo delta."""
        if self.stage in (PlantStage.EMPTY, PlantStage.READY):
            return

        self.growth_progress += dt / self._growth_time
        self.growth_progress = min(self.growth_progress, 1.0)

        # Determinar etapa visual según progreso
        if self.growth_progress < 0.25:
            self.stage = PlantStage.SEED
        elif self.growth_progress < 0.60:
            self.stage = PlantStage.SPROUT
        elif self.growth_progress < 1.0:
            self.stage = PlantStage.GROWING
        else:
            self.stage = PlantStage.READY

    def harvest(self) -> str | None:
        """Cosecha la flor si está lista. Reinicia la maceta."""
        if self.stage != PlantStage.READY:
            return None
        harvested = self.flower_type
        self.flower_type = None
        self.stage = PlantStage.EMPTY
        self.growth_progress = 0.0
        return harvested

    def draw(self, surface, camera_x: int, camera_y: int, time_elapsed: float):
        """Dibuja la planta en la posición de pantalla con animación suave."""
        import pygame
        if self.stage == PlantStage.EMPTY:
            return

        # Posición en píxeles
        sx = self.col * TILE_SIZE - camera_x + TILE_SIZE // 2
        sy = self.row * TILE_SIZE - camera_y + TILE_SIZE // 2

        # Oscilación del tallo
        sway = math.sin(time_elapsed * 1.5 + self._anim_offset) * 1.5

        colors = FLOWER_COLORS.get(self.flower_type, FLOWER_COLORS["daisy"])
        stem_color  = colors["stem"]
        petal_color = colors["petal"]
        center_color= colors["center"]

        if self.stage == PlantStage.SEED:
            # Pequeño bulto marrón
            pygame.draw.ellipse(surface, (120, 80, 40),
                                (sx - 3, sy + 8, 6, 4))

        elif self.stage == PlantStage.SPROUT:
            # Tallo corto + dos hojitas
            h = int(10 * self.growth_progress / 0.6)
            pygame.draw.line(surface, stem_color,
                             (sx + int(sway), sy + 12),
                             (sx + int(sway), sy + 12 - h), 2)
            # Hojitas
            pygame.draw.ellipse(surface, stem_color,
                                (sx - 5 + int(sway), sy + 8 - h, 5, 3))
            pygame.draw.ellipse(surface, stem_color,
                                (sx + 1 + int(sway), sy + 8 - h, 5, 3))

        elif self.stage in (PlantStage.GROWING, PlantStage.READY):
            # Tallo completo
            stem_top_y = sy - 4
            pygame.draw.line(surface, stem_color,
                             (sx + int(sway), sy + 14),
                             (sx + int(sway), stem_top_y), 2)

            # Hojas laterales
            pygame.draw.ellipse(surface, stem_color,
                                (sx - 10 + int(sway), sy, 10, 5))
            pygame.draw.ellipse(surface, stem_color,
                                (sx + 1 + int(sway), sy + 3, 10, 5))

            # Cabeza de la flor
            if self.stage == PlantStage.READY:
                # Flor completamente abierta
                _draw_flower_head(surface, sx + int(sway), stem_top_y,
                                  petal_color, center_color, 8)
            else:
                # Brote parcialmente abierto
                size = int(4 + 4 * (self.growth_progress - 0.6) / 0.4)
                _draw_flower_head(surface, sx + int(sway), stem_top_y,
                                  petal_color, center_color, size)

    def to_dict(self) -> dict:
        return {
            "col": self.col, "row": self.row,
            "flower_type": self.flower_type,
            "stage": int(self.stage),
            "growth_progress": self.growth_progress,
            "growth_time": self._growth_time,
        }

    def from_dict(self, data: dict):
        self.flower_type     = data.get("flower_type")
        self.stage           = PlantStage(data.get("stage", 0))
        self.growth_progress = data.get("growth_progress", 0.0)
        self._growth_time    = data.get("growth_time", 30.0)


def _draw_flower_head(surface, cx: int, cy: int,
                      petal_col, center_col, size: int):
    """Dibuja una flor estilizada con pétalos circulares alrededor."""
    import pygame
    for i in range(6):
        angle = math.radians(i * 60)
        px = cx + int(math.cos(angle) * size)
        py = cy + int(math.sin(angle) * size)
        pygame.draw.circle(surface, petal_col, (px, py), max(size - 2, 3))
    pygame.draw.circle(surface, center_col, (cx, cy), max(size // 2, 2))


class PlantManager:
    """
    Administra todas las macetas del jardín. Proporciona métodos para
    plantar, actualizar, cosechar y renderizar las plantas.
    """

    def __init__(self):
        # Crear macetas en las posiciones del jardín definidas en config
        self.plants: list[Plant] = [
            Plant(col, row) for col, row in GARDEN_AREA
        ]

    def get_plant_at(self, col: int, row: int) -> Plant | None:
        """Retorna la maceta en una posición de la cuadrícula, o None."""
        for plant in self.plants:
            if plant.col == col and plant.row == row:
                return plant
        return None

    def get_empty_plant(self) -> Plant | None:
        """Retorna la primera maceta vacía disponible."""
        for plant in self.plants:
            if plant.stage == PlantStage.EMPTY:
                return plant
        return None

    def get_ready_plants(self) -> list[Plant]:
        """Retorna todas las plantas listas para cosechar."""
        return [p for p in self.plants if p.stage == PlantStage.READY]

    def update(self, dt: float, time_elapsed: float):
        for plant in self.plants:
            plant.update(dt, time_elapsed)

    def draw(self, surface, camera_x: int, camera_y: int, time_elapsed: float):
        for plant in self.plants:
            plant.draw(surface, camera_x, camera_y, time_elapsed)

    def to_dict(self) -> list:
        return [p.to_dict() for p in self.plants]

    def from_dict(self, data: list):
        for pdata in data:
            plant = self.get_plant_at(pdata["col"], pdata["row"])
            if plant:
                plant.from_dict(pdata)
