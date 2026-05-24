import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS, FLOWER_DATA


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

        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class UIPanel:
    def __init__(self):
        self.buttons = []
        self.info_text = []

    def add_button(self, button):
        self.buttons.append(button)

    def update(self, inventory, garden, customers):
        self.info_text = [
            f"Dinero: ${inventory.money:.0f}",
            f"Flores: {inventory.get_total_flowers()}",
            f"Plantas: {len(garden.plants)}",
            f"Clientes: {len(customers.customers)}",
            f"Atractivo: {getattr(customers.shop, 'attractiveness', 50)}",
            "",
            "CONTROLES:",
            "WASD: Mover",
            "E: Interactuar",
            "1-4: Semillas"
        ]

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def draw(self, screen):
        panel_rect = pygame.Rect(10, 10, 280, 700)
        pygame.draw.rect(screen, COLORS['ui_bg'], panel_rect)
        pygame.draw.rect(screen, COLORS['ui_border'], panel_rect, 3)

        font = pygame.font.Font(None, 22)
        for i, text in enumerate(self.info_text):
            surf = font.render(text, True, COLORS['text'])
            screen.blit(surf, (20, 20 + i * 25))

        for button in self.buttons:
            button.draw(screen)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🌸 Floristería Cozy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        from .player import Player
        from .inventory import Inventory
        from .plants import Garden
        from .shop import Shop
        from .customer import CustomerManager

        self.player = Player()
        self.inventory = Inventory()
        self.garden = Garden()
        self.shop = Shop()
        self.customers = CustomerManager()
        self.customers.shop = self.shop  # Fix referencia circular
        self.ui = UIPanel()

        self.state = "playing"
        self.camera_offset = [0, 0]
        self.day_time = 0
        self.keys = {}

        self.setup_ui()
        self.inventory.load("data/save.json")

    def setup_ui(self):
        def buy_seed(plant_type):
            price = FLOWER_DATA[plant_type]['price'] * 0.5
            self.inventory.buy_seeds(plant_type, 1, price)

        self.ui.add_button(Button(20, 500, 260, 40, "🌹 Rosa ($2)",
                                  lambda: buy_seed('rosa')))
        self.ui.add_button(Button(20, 550, 260, 40, "🌼 Margarita ($1)",
                                  lambda: buy_seed('margarita')))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.interact(
                        self.shop, self.garden, self.inventory)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "paused" if self.state == "playing" else "playing"
            self.ui.handle_event(event)

    def update(self, dt):
        self.keys = pygame.key.get_pressed()

        if self.state == "playing":
            self.player.update(self.keys, dt)
            self.garden.update()
            self.shop.update()
            self.customers.update(self.shop.shelves, self.shop.cashier_pos, dt)

            self.camera_offset[0] = max(
                0, self.player.rect.centerx - SCREEN_WIDTH//2)
            self.camera_offset[1] = max(
                0, self.player.rect.centery - SCREEN_HEIGHT//2)

            self.day_time += dt * 60
            if self.day_time > 1440:
                self.day_time = 0

        self.ui.update(self.inventory, self.garden, self.customers)

    def draw(self):
        hour = int(self.day_time / 60)
        bg_color = COLORS['bg_night'] if (
            18 <= hour or hour <= 6) else COLORS['bg_day']
        self.screen.fill(bg_color)

        pygame.draw.rect(self.screen, COLORS['grass'], (50, 400, 300, 250))

        self.garden.draw(self.screen, self.camera_offset)
        self.shop.draw(self.screen, self.camera_offset)
        self.customers.draw(self.screen, self.camera_offset)
        self.player.draw(self.screen, self.camera_offset)
        self.ui.draw(self.screen)

        if self.state == "paused":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            text = self.font.render("PAUSADO - ESC", True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def quit(self):
        self.inventory.save("data/save.json")
        pygame.quit()
        sys.exit()


# Fix para import circular en CustomerManager
sys.modules['src.shop'] = Shop()