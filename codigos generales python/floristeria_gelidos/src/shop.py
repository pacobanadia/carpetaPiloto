import pygame
from typing import List

class Shelf:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 64, 48)
        self.stock = 0
        self.max_stock = 5
        self.price = 6.0
    
    def draw(self, screen, camera_offset=(0,0)):
        x, y = self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]
        
        # Estante base
        pygame.draw.rect(screen, (139, 69, 19), (x, y+32, 64, 16))  # Base
        pygame.draw.rect(screen, (205, 133, 63), (x+4, y, 56, 36))   # Estante
        
        # Flores
        for i in range(min(self.stock, 3)):
            fx = x + 12 + i * 16
            pygame.draw.circle(screen, (255, 20, 147), (fx, y+12), 6)
    
    def restock(self, amount: int):
        self.stock = min(self.stock + amount, self.max_stock)

class Shop:
    def __init__(self):
        self.shelves: List[Shelf] = []
        self.cashier_pos = (900, 250)
        self.decor_level = 1
        self.attractiveness = 50
        
        # Crear estantes
        for i in range(4):
            shelf = Shelf(400 + i * 120, 200)
            self.shelves.append(shelf)
            shelf2 = Shelf(400 + i * 120, 350)
            self.shelves.append(shelf2)
    
    def update(self):
        # Actualizar atractivo basado en decoración y stock
        total_stock = sum(s.stock for s in self.shelves)
        self.attractiveness = 30 + self.decor_level * 10 + min(total_stock * 2, 20)
    
    def draw(self, screen, camera_offset=(0,0)):
        # Fondo de tienda
        shop_rect = pygame.Rect(200, 100, 880, 500)
        x1, y1 = shop_rect.x - camera_offset[0], shop_rect.y - camera_offset[1]
        pygame.draw.rect(screen, (248, 222, 126), (x1, y1, shop_rect.width, shop_rect.height))
        pygame.draw.rect(screen, (160, 82, 45), (x1, y1, shop_rect.width, 8), 4)  # Borde
        
        # Caja registradora
        cx, cy = self.cashier_pos[0] - camera_offset[0], self.cashier_pos[1] - camera_offset[1]
        pygame.draw.rect(screen, (169, 169, 169), (cx-20, cy-15, 40, 30))
        pygame.draw.rect(screen, (0, 0, 0), (cx-10, cy-5, 20, 10))
        
        # Estantes
        for shelf in self.shelves:
            shelf.draw(screen, camera_offset)
    
    def get_shelf_at(self, pos):
        for shelf in self.shelves:
            if shelf.rect.collidepoint(pos):
                return shelf
        return None