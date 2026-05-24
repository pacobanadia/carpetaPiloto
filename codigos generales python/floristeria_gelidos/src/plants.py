import pygame
import random
from enum import Enum
from typing import List, Dict
from config import FLOWER_DATA

class PlantState(Enum):
    SEED = 0
    GROWING = 1
    READY = 2
    HARVESTED = 3

class Plant:
    def __init__(self, plant_type: str, x: int, y: int):
        self.type = plant_type
        self.state = PlantState.SEED
        self.x = x
        self.y = y
        self.plant_time = pygame.time.get_ticks()
        self.growth_time = FLOWER_DATA[plant_type]['growth_time'] * 1000  # ms
        
    def update(self):
        """Actualizar estado de crecimiento"""
        current_time = pygame.time.get_ticks()
        if self.state == PlantState.SEED and current_time - self.plant_time > self.growth_time * 0.5:
            self.state = PlantState.GROWING
        elif self.state == PlantState.GROWING and current_time - self.plant_time > self.growth_time:
            self.state = PlantState.READY
    
    def draw(self, screen, camera_offset):
        x, y = self.x - camera_offset[0], self.y - camera_offset[1]
        
        color = FLOWER_DATA[self.type]['color']
        
        if self.state == PlantState.SEED:
            pygame.draw.circle(screen, (139, 69, 19), (x+8, y+8), 4)  # Semilla
        elif self.state == PlantState.GROWING:
            pygame.draw.rect(screen, (34, 139, 34), (x+12, y+16, 8, 12))  # Tallo
            pygame.draw.circle(screen, color, (x+16, y+8), 6)  # Brote
        elif self.state == PlantState.READY:
            pygame.draw.rect(screen, (34, 139, 34), (x+12, y+16, 8, 12))  # Tallo
            pygame.draw.circle(screen, color, (x+16, y+8), 10)  # Flor
        
        # Maceta
        pygame.draw.rect(screen, (160, 82, 45), (x, y, 32, 8))
    
    def harvest(self) -> str:
        """Cosechar planta madura"""
        if self.state == PlantState.READY:
            self.state = PlantState.HARVESTED
            return f"flor_{self.type}"
        return None

class Garden:
    def __init__(self):
        self.plants: List[Plant] = []
        self.grid = [[None for _ in range(10)] for _ in range(6)]  # 6x10 grid
        
    def plant(self, plant_type: str, grid_x: int, grid_y: int) -> bool:
        """Plantar nueva semilla"""
        if 0 <= grid_x < 10 and 0 <= grid_y < 6 and self.grid[grid_y][grid_x] is None:
            x = 80 + grid_x * 32
            y = 450 + grid_y * 32
            plant = Plant(plant_type, x, y)
            self.plants.append(plant)
            self.grid[grid_y][grid_x] = plant
            return True
        return False
    
    def update(self):
        for plant in self.plants[:]:
            plant.update()
            if plant.state == PlantState.HARVESTED:
                self.plants.remove(plant)
                grid_x = (plant.x - 80) // 32
                grid_y = (plant.y - 450) // 32
                self.grid[grid_y][grid_x] = None
    
    def draw(self, screen, camera_offset=(0,0)):
        for plant in self.plants:
            plant.draw(screen, camera_offset)
    
    def get_plant_at(self, pos) -> Plant:
        grid_x = (pos[0] - 80) // 32
        grid_y = (pos[1] - 450) // 32
        if 0 <= grid_x < 10 and 0 <= grid_y < 6:
            return self.grid[grid_y][grid_x]
        return None