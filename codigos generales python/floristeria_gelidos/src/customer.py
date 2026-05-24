import pygame
import random
import math
from enum import Enum
from typing import List

class CustomerState(Enum):
    ENTERING = 0
    BROWSING = 1
    AT_SHELF = 2
    TO_CASHIER = 3
    WAITING = 4
    LEAVING = 5

class Customer:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 28, 28)
        self.state = CustomerState.ENTERING
        self.target_pos = (0, 0)
        self.speed = 1.2
        self.patience = 100
        self.items_wanted = random.randint(1, 3)
        self.items_bought = 0
        self.entry_time = pygame.time.get_ticks()
        self.spawn()
    
    def spawn(self):
        """Aparecer en entrada"""
        self.rect.x = 250
        self.rect.y = 120
        self.state = CustomerState.ENTERING
    
    def update(self, shelves: List, cashier_pos, dt: float):
        self.patience -= dt * 0.1
        
        if self.patience <= 0:
            self.state = CustomerState.LEAVING
            return
        
        if self.state == CustomerState.ENTERING:
            self.state = CustomerState.BROWSING
        
        elif self.state == CustomerState.BROWSING:
            if random.random() < 0.02:  # Elegir estante aleatorio
                shelf = random.choice([s for s in shelves if s.stock > 0])
                if shelf:
                    self.target_pos = shelf.rect.center
                    self.state = CustomerState.AT_SHELF
        
        elif self.state == CustomerState.AT_SHELF:
            distance = math.hypot(self.rect.centerx - self.target_pos[0], 
                                self.rect.centery - self.target_pos[1])
            if distance < 40:
                if random.random() < 0.1 and self.items_bought < self.items_wanted:
                    self.items_bought += 1
                    self.state = CustomerState.TO_CASHIER
                else:
                    self.state = CustomerState.BROWSING
            else:
                self.move_towards(self.target_pos)
        
        elif self.state == CustomerState.TO_CASHIER:
            distance = math.hypot(self.rect.centerx - cashier_pos[0], 
                                self.rect.centery - cashier_pos[1])
            if distance < 50:
                self.state = CustomerState.WAITING
            else:
                self.move_towards(cashier_pos)
        
        elif self.state == CustomerState.LEAVING:
            self.move_towards((300, 50))
            if self.rect.top < 0:
                self.remove = True
    
    def move_towards(self, target):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx/dist, dy/dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
    
    def draw(self, screen, camera_offset=(0,0)):
        x, y = self.rect.centerx - camera_offset[0], self.rect.centery - camera_offset[1]
        
        # Cuerpo del cliente (estilo Animal Crossing)
        pygame.draw.ellipse(screen, (255, 182, 193), (x-12, y-10, 24, 20))  # Cabeza
        pygame.draw.rect(screen, random.choice([(255, 105, 180), (100, 149, 237), 
                                               (255, 218, 185)]), 
                        (x-10, y+2, 20, 22))  # Ropa
        
        # Burbuja de paciencia
        if self.state == CustomerState.WAITING:
            patience_color = (0, 255, 0) if self.patience > 50 else (255, 165, 0)
            pygame.draw.circle(screen, patience_color, (x, y-25), 8)
    
    def serve(self):
        """Atender cliente en caja"""
        self.state = CustomerState.LEAVING
        return self.items_bought * 6  # Ganancia por item

class CustomerManager:
    def __init__(self):
        self.customers: List[Customer] = []
        self.last_spawn = 0
        self.spawn_timer = 0
    
    def update(self, shelves, cashier_pos, dt):
        self.spawn_timer += dt
        if self.spawn_timer > 10 and len(self.customers) < 3 and random.random() < 0.3:
            self.customers.append(Customer())
            self.spawn_timer = 0
        
        for customer in self.customers[:]:
            customer.update(shelves, cashier_pos, dt)
            if hasattr(customer, 'remove') and customer.remove:
                self.customers.remove(customer)
    
    def draw(self, screen, camera_offset):
        for customer in self.customers:
            customer.draw(screen, camera_offset)
    
    def get_waiting_customers(self):
        return [c for c in self.customers if c.state == CustomerState.WAITING]