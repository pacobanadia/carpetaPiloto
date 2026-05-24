import pygame
from enum import Enum

class PlayerState(Enum):
    IDLE = 0
    WALKING = 1
    INTERACTING = 2

class Player:
    def __init__(self, x=100, y=100):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 2
        self.state = PlayerState.IDLE
        self.facing = 'down'  # down, up, left, right
        self.inventory_held = None  # Item siendo cargado
        
    def update(self, keys, dt):
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.facing = 'left'
            self.state = PlayerState.WALKING
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.facing = 'right'
            self.state = PlayerState.WALKING
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
            self.facing = 'up'
            self.state = PlayerState.WALKING
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.facing = 'down'
            self.state = PlayerState.WALKING
        
        # Diagonales normalizados
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        self.rect.x += dx
        self.rect.y += dy
        
        # Mantener en bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 720))
        
        # Volver a idle si no se mueve
        if dx == 0 and dy == 0:
            self.state = PlayerState.IDLE
    
    def draw(self, screen, camera_offset=(0,0)):
        x, y = self.rect.centerx - camera_offset[0], self.rect.centery - camera_offset[1]
        
        # Cuerpo
        pygame.draw.ellipse(screen, (255, 224, 189), (x-12, y-8, 24, 20))  # Cara
        pygame.draw.rect(screen, (0, 100, 0), (x-10, y+4, 20, 24))         # Delantal
        
        # Animación simple de caminar
        if self.state == PlayerState.WALKING:
            offset = int(pygame.time.get_ticks() / 100) % 2
            pygame.draw.circle(screen, (255, 20, 147), (x + offset*4 - 4, y+24), 4)  # Pie
            
        # Item en mano
        if self.inventory_held:
            pygame.draw.circle(screen, (255, 255, 0), (x+16, y-8), 8)
    
    def interact(self, shop, garden, inventory):
        """Interactuar con objetos cercanos"""
        player_pos = self.rect.center
        
        # Estantes
        for shelf in shop.shelves:
            if shelf.rect.collidepoint(player_pos) and inventory.get_total_flowers() > 0:
                flower_type = "rosa"  # Simplificado
                if inventory.remove_item(f"flor_{flower_type}", 1):
                    shelf.stock += 1
                    return True
        
        # Plantas
        plant = garden.get_plant_at(player_pos)
        if plant and plant.state == PlantState.READY:
            flower_type = plant.harvest()
            if flower_type:
                inventory.add_item(flower_type, 1, 5.0)
                return True
        
        return False