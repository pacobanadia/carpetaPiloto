import pygame
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, FLOWER_DATA

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return False
    
    def draw(self, screen):
        color = COLORS['success'] if self.hovered else COLORS['ui_bg']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS['ui_border'], self.rect, 2)
        
        # Texto centrado
        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class UIPanel:
    def __init__(self):
        self.buttons: list = []
        self.info_text = []
        
    def add_button(self, button: Button):
        self.buttons.append(button)
    
    def update(self, inventory, garden, shop):
        self.info_text = [
            f"Dinero: ${inventory.money:.0f}",
            f"Flores: {inventory.get_total_flowers()}",
            f"Plantas: {len(garden.plants)}",
            f"Clientes: {len([c for c in shop.customers if hasattr(c, 'customers')])}",  # Fix needed
            f"Atractivo: {shop.attractiveness}",
            "",
            "CONTROLES:",
            "WASD: Mover",
            "E: Interactuar",
            "1-4: Comprar semillas"
        ]
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def draw(self, screen):
        # Panel de fondo
        panel_rect = pygame.Rect(10, 10, 280, 700)
        pygame.draw.rect(screen, COLORS['ui_bg'], panel_rect)
        pygame.draw.rect(screen, COLORS['ui_border'], panel_rect, 3)
        
        # Información
        font = pygame.font.Font(None, 22)
        for i, text in enumerate(self.info_text):
            surf = font.render(text, True, COLORS['text'])
            screen.blit(surf, (20, 20 + i * 25))
        
        # Botones
        for button in self.buttons:
            button.draw(screen)

class ShopUI:
    def __init__(self):
        self.visible = False
        self.selected_price = 6.0
        
    def draw(self, screen):
        if not self.visible:
            return
            
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))
        
        # Panel de precios
        panel_rect = pygame.Rect(400, 200, 300, 200)
        pygame.draw.rect(screen, COLORS['ui_bg'], panel_rect)
        pygame.draw.rect(screen, COLORS['ui_border'], panel_rect, 3)
        
        font = pygame.font.Font(None, 32)
        text = font.render("Ajustar Precio", True, COLORS['text'])
        screen.blit(text, (450, 220))
        
        price_text = font.render(f"${self.selected_price:.1f}", True, COLORS['success'])
        screen.blit(price_text, (480, 280))