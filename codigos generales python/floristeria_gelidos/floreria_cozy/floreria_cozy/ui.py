"""
ui.py — Interfaz de usuario del juego
======================================
Renderiza el HUD principal (dinero, día, hora, reputación),
el menú de compra de semillas, el panel de inventario,
el panel de ajuste de precios y notificaciones flotantes.

Clase principal:
    UI — Gestor de toda la interfaz
"""

import pygame
import math
from config import (
    COLOR_UI_BG, COLOR_UI_PANEL, COLOR_UI_BORDER, COLOR_UI_ACCENT,
    COLOR_UI_TEXT, COLOR_UI_TEXT_LIGHT, COLOR_UI_BUTTON, COLOR_UI_BTN_HOVER,
    COLOR_UI_BTN_PRESS, COLOR_UI_SUCCESS, COLOR_UI_DANGER, COLOR_UI_GOLD,
    SEED_PRICES, FLOWER_SELL_PRICES, FLOWER_COLORS, WINDOW_WIDTH, WINDOW_HEIGHT,
    DAY_DURATION,
)


class Button:
    """Botón interactivo reutilizable."""

    def __init__(self, x, y, w, h, text, color=None, text_color=None, font_size=15):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color      = color      or COLOR_UI_BUTTON
        self.text_color = text_color or COLOR_UI_TEXT
        self.font = pygame.font.SysFont("segoeui", font_size, bold=True)
        self.hovered = False
        self.pressed = False

    def handle_event(self, event) -> bool:
        """Retorna True si fue clicado."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
        return False

    def draw(self, surface):
        color = self.color
        if self.pressed:
            color = COLOR_UI_BTN_PRESS
        elif self.hovered:
            color = COLOR_UI_BTN_HOVER

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_UI_BORDER, self.rect, border_radius=8, width=2)

        # Sombra interna inferior
        shadow = pygame.Rect(self.rect.x + 2, self.rect.bottom - 4,
                             self.rect.width - 4, 3)
        pygame.draw.rect(surface, (*COLOR_UI_BORDER, 80), shadow, border_radius=4)

        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))


class Notification:
    """Notificación flotante con desvanecimiento."""

    def __init__(self, text: str, x: int, y: int,
                 color=(80, 150, 80), duration=2.0):
        self.text     = text
        self.x        = float(x)
        self.y        = float(y)
        self.color    = color
        self.timer    = duration
        self.duration = duration
        self.font     = pygame.font.SysFont("segoeui", 16, bold=True)

    def update(self, dt: float) -> bool:
        """Retorna False cuando debe eliminarse."""
        self.timer -= dt
        self.y     -= 25 * dt  # Sube lentamente
        return self.timer > 0

    def draw(self, surface):
        alpha = max(0, int(255 * (self.timer / self.duration)))
        txt = self.font.render(self.text, True, self.color)
        txt.set_alpha(alpha)
        surface.blit(txt, (int(self.x) - txt.get_width() // 2, int(self.y)))


class UI:
    """
    Gestor de la interfaz completa del juego. Coordina:
    - HUD principal
    - Menú de semillas (tienda del proveedor)
    - Panel de inventario
    - Panel de ajuste de precios
    - Notificaciones flotantes
    - Pantalla de resumen de día
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h

        # Fuentes
        self.font_xl   = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_lg   = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_md   = pygame.font.SysFont("segoeui", 16)
        self.font_sm   = pygame.font.SysFont("segoeui", 13)
        self.font_bold = pygame.font.SysFont("segoeui", 14, bold=True)

        # Estado de paneles
        self.show_seed_shop  = False
        self.show_inventory  = False
        self.show_price_panel= False
        self.show_day_summary= False

        # Datos del resumen de día
        self.day_summary = {}

        # Botones del HUD
        self.btn_seeds   = Button(10, self.sh - 55, 120, 42, "🌱 Semillas")
        self.btn_inv     = Button(140, self.sh - 55, 120, 42, "🌸 Inventario")
        self.btn_prices  = Button(270, self.sh - 55, 120, 42, "💰 Precios")

        # Notificaciones flotantes
        self.notifications: list[Notification] = []

        # Índice de estante seleccionado para precio
        self._selected_shelf_idx = 0

        # Scroll en el panel de semillas
        self._seed_scroll = 0

        # Botón de continuar en resumen de día
        self.btn_next_day = Button(self.sw // 2 - 80, self.sh // 2 + 120,
                                   160, 44, "▶ Siguiente día")

    # ── Notificaciones ────────────────────────────────────────

    def notify(self, text: str, x: int = None, y: int = None,
               color=(80, 150, 80)):
        """Agrega una notificación flotante en pantalla."""
        nx = x if x is not None else self.sw // 2
        ny = y if y is not None else self.sh // 2 - 50
        self.notifications.append(Notification(text, nx, ny, color))

    # ── Actualización ─────────────────────────────────────────

    def update(self, dt: float):
        self.notifications = [n for n in self.notifications if n.update(dt)]

    # ── Manejo de eventos ─────────────────────────────────────

    def handle_event(self, event, game_state: dict) -> dict:
        """
        Procesa eventos de UI. Retorna un dict con acciones solicitadas:
        {buy_seed: str, toggle_panel: str, price_change: (shelf_idx, delta), etc.}
        """
        actions = {}

        # Botones del HUD
        if self.btn_seeds.handle_event(event):
            self.show_seed_shop   = not self.show_seed_shop
            self.show_inventory   = False
            self.show_price_panel = False
        if self.btn_inv.handle_event(event):
            self.show_inventory   = not self.show_inventory
            self.show_seed_shop   = False
            self.show_price_panel = False
        if self.btn_prices.handle_event(event):
            self.show_price_panel = not self.show_price_panel
            self.show_seed_shop   = False
            self.show_inventory   = False

        # Panel de semillas
        if self.show_seed_shop:
            result = self._handle_seed_shop(event, game_state)
            if result:
                actions.update(result)

        # Panel de precios
        if self.show_price_panel:
            result = self._handle_price_panel(event, game_state)
            if result:
                actions.update(result)

        # Resumen de día
        if self.show_day_summary:
            if self.btn_next_day.handle_event(event):
                actions["next_day"] = True
                self.show_day_summary = False

        return actions

    def _handle_seed_shop(self, event, gs) -> dict | None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        mx, my = event.pos
        # Panel en el centro
        px = self.sw // 2 - 200
        py = self.sh // 2 - 220

        for i, (flower, price) in enumerate(SEED_PRICES.items()):
            btn_rect = pygame.Rect(px + 10, py + 60 + i * 48, 380, 40)
            if btn_rect.collidepoint(mx, my):
                return {"buy_seed": flower, "seed_price": price}
        return None

    def _handle_price_panel(self, event, gs) -> dict | None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        mx, my = event.pos
        px = self.sw - 240
        py = 80
        shelves = gs.get("shelves", [])
        for i, shelf in enumerate(shelves):
            y_pos = py + 50 + i * 60
            # Botón -
            if pygame.Rect(px + 10, y_pos + 20, 30, 24).collidepoint(mx, my):
                return {"price_change": (i, -1)}
            # Botón +
            if pygame.Rect(px + 160, y_pos + 20, 30, 24).collidepoint(mx, my):
                return {"price_change": (i, 1)}
        return None

    # ── Renderizado principal ─────────────────────────────────

    def draw(self, surface, game_state: dict):
        """Dibuja toda la UI sobre el frame renderizado del juego."""
        self._draw_hud(surface, game_state)
        self._draw_action_hints(surface, game_state)

        if self.show_seed_shop:
            self._draw_seed_shop(surface, game_state)
        if self.show_inventory:
            self._draw_inventory(surface, game_state)
        if self.show_price_panel:
            self._draw_price_panel(surface, game_state)
        if self.show_day_summary:
            self._draw_day_summary(surface)

        # Botones del HUD
        self.btn_seeds.draw(surface)
        self.btn_inv.draw(surface)
        self.btn_prices.draw(surface)

        # Notificaciones
        for notif in self.notifications:
            notif.draw(surface)

    def _draw_hud(self, surface, gs: dict):
        """HUD superior con dinero, día, hora y reputación."""
        # Panel superior
        hud_rect = pygame.Rect(0, 0, self.sw, 54)
        hud_surf = pygame.Surface((self.sw, 54), pygame.SRCALPHA)
        hud_surf.fill((255, 248, 230, 220))
        surface.blit(hud_surf, (0, 0))
        pygame.draw.line(surface, COLOR_UI_BORDER, (0, 54), (self.sw, 54), 2)

        # Dinero
        money = gs.get("money", 0.0)
        money_txt = self.font_xl.render(f"💰 ${money:,.0f}", True, (60, 120, 60))
        surface.blit(money_txt, (16, 10))

        # Día
        day = gs.get("day", 1)
        day_txt = self.font_lg.render(f"Día {day}", True, COLOR_UI_TEXT)
        surface.blit(day_txt, (self.sw // 2 - day_txt.get_width() // 2, 8))

        # Hora (ciclo día)
        time_of_day = gs.get("time_of_day", 0.0)
        hour  = int(8 + (time_of_day / DAY_DURATION) * 12)
        mins  = int(((time_of_day / DAY_DURATION) * 12 * 60) % 60)
        ampm  = "AM" if hour < 12 else "PM"
        hour12= hour if hour <= 12 else hour - 12
        time_str = f"🕐 {hour12:02d}:{mins:02d} {ampm}"
        time_txt = self.font_lg.render(time_str, True, COLOR_UI_TEXT)
        surface.blit(time_txt, (self.sw // 2 - time_txt.get_width() // 2, 30))

        # Reputación
        rep = gs.get("reputation", 50.0)
        self._draw_reputation_bar(surface, self.sw - 230, 12, 210, 14, rep)
        rep_txt = self.font_sm.render(f"Reputación: {rep:.0f}/100", True, COLOR_UI_TEXT)
        surface.blit(rep_txt, (self.sw - 220, 30))

        # Estado de la tienda
        store_open = gs.get("store_open", True)
        status_color = (80, 180, 80) if store_open else (180, 80, 80)
        status_txt   = self.font_bold.render(
            "ABIERTA" if store_open else "CERRADA", True, status_color)
        surface.blit(status_txt, (self.sw - 80, 10))

    def _draw_reputation_bar(self, surface, x, y, w, h, value):
        bg_rect  = pygame.Rect(x, y, w, h)
        fill_w   = int(w * value / 100)
        fill_rect= pygame.Rect(x, y, fill_w, h)
        color = (90, 200, 90) if value > 60 else (220, 180, 50) if value > 30 else (220, 60, 60)
        pygame.draw.rect(surface, (200, 180, 160), bg_rect, border_radius=4)
        pygame.draw.rect(surface, color, fill_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_UI_BORDER, bg_rect, border_radius=4, width=1)

    def _draw_action_hints(self, surface, gs: dict):
        """Pistas de acción según el contexto del jugador."""
        hints = gs.get("hints", [])
        if not hints:
            return
        hint_surf = pygame.Surface((self.sw, 28), pygame.SRCALPHA)
        hint_surf.fill((60, 40, 20, 160))
        surface.blit(hint_surf, (0, self.sh - 90))
        text = "  |  ".join(hints)
        txt = self.font_sm.render(text, True, (255, 235, 190))
        surface.blit(txt, (self.sw // 2 - txt.get_width() // 2, self.sh - 84))

    def _draw_seed_shop(self, surface, gs: dict):
        """Menú de compra de semillas al proveedor."""
        px = self.sw // 2 - 200
        py = self.sh // 2 - 220
        panel = pygame.Surface((400, 440), pygame.SRCALPHA)
        panel.fill((*COLOR_UI_PANEL, 245))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, COLOR_UI_BORDER, (px, py, 400, 440),
                         border_radius=10, width=3)

        # Título
        title = self.font_xl.render("🌱 Proveedor de Semillas", True, COLOR_UI_TEXT)
        surface.blit(title, (px + 200 - title.get_width() // 2, py + 12))

        money = gs.get("money", 0.0)
        mon_txt = self.font_md.render(f"Fondos: ${money:,.0f}", True, (60, 120, 60))
        surface.blit(mon_txt, (px + 200 - mon_txt.get_width() // 2, py + 42))

        for i, (flower, price) in enumerate(SEED_PRICES.items()):
            fy = py + 70 + i * 52
            colors = FLOWER_COLORS.get(flower, FLOWER_COLORS["daisy"])
            can_buy = money >= price

            # Fondo del item
            item_color = COLOR_UI_BG if can_buy else (230, 220, 215)
            pygame.draw.rect(surface, item_color, (px + 8, fy, 384, 44), border_radius=8)
            pygame.draw.rect(surface, COLOR_UI_BORDER, (px + 8, fy, 384, 44), border_radius=8, width=1)

            # Flor decorativa
            for j in range(5):
                angle = math.radians(j * 72)
                fx2 = px + 30 + int(math.cos(angle) * 8)
                fy2 = fy + 22 + int(math.sin(angle) * 8)
                pygame.draw.circle(surface, colors["petal"], (fx2, fy2), 4)
            pygame.draw.circle(surface, colors["center"], (px + 30, fy + 22), 4)

            # Nombre
            name_txt = self.font_lg.render(flower.capitalize(), True,
                                           COLOR_UI_TEXT if can_buy else (160, 140, 120))
            surface.blit(name_txt, (px + 48, fy + 8))

            # Precio
            price_txt = self.font_md.render(f"${price:.0f}", True,
                                            (60, 120, 60) if can_buy else (160, 100, 80))
            surface.blit(price_txt, (px + 280, fy + 12))

            # Semillas en inventario
            seeds = gs.get("seeds", {}).get(flower, 0)
            seed_txt = self.font_sm.render(f"Tienes: {seeds}", True, COLOR_UI_TEXT_LIGHT)
            surface.blit(seed_txt, (px + 320, fy + 14))

            # Indicador visual de "comprar"
            btn_color = COLOR_UI_ACCENT if can_buy else (180, 160, 140)
            pygame.draw.rect(surface, btn_color, (px + 350, fy + 10, 36, 24), border_radius=6)
            plus = self.font_lg.render("+", True, (255, 255, 255))
            surface.blit(plus, (px + 362, fy + 10))

        # Cerrar
        close_txt = self.font_sm.render("[Clic en 🌱 para cerrar]", True, COLOR_UI_TEXT_LIGHT)
        surface.blit(close_txt, (px + 200 - close_txt.get_width() // 2, py + 412))

    def _draw_inventory(self, surface, gs: dict):
        """Panel de inventario del jugador."""
        px = self.sw // 2 - 180
        py = 70
        panel = pygame.Surface((360, 320), pygame.SRCALPHA)
        panel.fill((*COLOR_UI_PANEL, 245))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, COLOR_UI_BORDER, (px, py, 360, 320),
                         border_radius=10, width=3)

        title = self.font_xl.render("🌸 Mi Inventario", True, COLOR_UI_TEXT)
        surface.blit(title, (px + 180 - title.get_width() // 2, py + 12))

        flowers = gs.get("flowers", {})
        seeds   = gs.get("seeds", {})

        if not flowers and not seeds:
            empty_txt = self.font_md.render("Inventario vacío", True, COLOR_UI_TEXT_LIGHT)
            surface.blit(empty_txt, (px + 180 - empty_txt.get_width() // 2, py + 140))
        else:
            # Flores cosechadas
            y_offset = py + 50
            if flowers:
                sec = self.font_bold.render("Flores cosechadas:", True, COLOR_UI_TEXT)
                surface.blit(sec, (px + 12, y_offset))
                y_offset += 22
                for flower, count in flowers.items():
                    colors = FLOWER_COLORS.get(flower, FLOWER_COLORS["daisy"])
                    pygame.draw.circle(surface, colors["petal"], (px + 20, y_offset + 8), 7)
                    pygame.draw.circle(surface, colors["center"], (px + 20, y_offset + 8), 3)
                    txt = self.font_md.render(f"{flower.capitalize()} × {count}", True, COLOR_UI_TEXT)
                    surface.blit(txt, (px + 34, y_offset))
                    y_offset += 26

            if seeds:
                y_offset += 8
                sec = self.font_bold.render("Semillas:", True, COLOR_UI_TEXT)
                surface.blit(sec, (px + 12, y_offset))
                y_offset += 22
                for flower, count in seeds.items():
                    txt = self.font_md.render(f"🌱 {flower.capitalize()} × {count}", True, COLOR_UI_TEXT)
                    surface.blit(txt, (px + 14, y_offset))
                    y_offset += 26

        cap = gs.get("inv_capacity", 20)
        total = sum(flowers.values()) if flowers else 0
        cap_txt = self.font_sm.render(f"Capacidad: {total}/{cap}", True, COLOR_UI_TEXT_LIGHT)
        surface.blit(cap_txt, (px + 12, py + 290))

    def _draw_price_panel(self, surface, gs: dict):
        """Panel lateral de ajuste de precios por estante."""
        px = self.sw - 245
        py = 60
        pw, ph = 240, min(len(gs.get("shelves", [])) * 62 + 70, 450)

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*COLOR_UI_PANEL, 240))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, COLOR_UI_BORDER, (px, py, pw, ph),
                         border_radius=10, width=2)

        title = self.font_lg.render("💰 Ajustar Precios", True, COLOR_UI_TEXT)
        surface.blit(title, (px + pw // 2 - title.get_width() // 2, py + 8))

        shelves = gs.get("shelves", [])
        for i, shelf_data in enumerate(shelves[:7]):  # Máx 7 visibles
            sy = py + 44 + i * 58
            flower = shelf_data.get("flower_type")
            price  = shelf_data.get("price", 0.0)
            stock  = shelf_data.get("stock", 0)

            pygame.draw.rect(surface, COLOR_UI_BG, (px + 6, sy, pw - 12, 50),
                             border_radius=6)
            pygame.draw.rect(surface, COLOR_UI_BORDER, (px + 6, sy, pw - 12, 50),
                             border_radius=6, width=1)

            if flower:
                colors = FLOWER_COLORS.get(flower, FLOWER_COLORS["daisy"])
                pygame.draw.circle(surface, colors["petal"], (px + 22, sy + 14), 8)
                pygame.draw.circle(surface, colors["center"], (px + 22, sy + 14), 3)
                name_txt = self.font_sm.render(
                    f"{flower[:8].capitalize()} ({stock})", True, COLOR_UI_TEXT)
                surface.blit(name_txt, (px + 34, sy + 6))
            else:
                name_txt = self.font_sm.render("(vacío)", True, COLOR_UI_TEXT_LIGHT)
                surface.blit(name_txt, (px + 14, sy + 6))

            # Controles de precio
            pygame.draw.rect(surface, COLOR_UI_DANGER, (px + 10, sy + 24, 28, 22),
                             border_radius=5)
            minus = self.font_lg.render("-", True, (255, 255, 255))
            surface.blit(minus, (px + 20, sy + 24))

            price_txt = self.font_bold.render(f"${price:.0f}", True, COLOR_UI_TEXT)
            surface.blit(price_txt, (px + pw // 2 - price_txt.get_width() // 2, sy + 26))

            pygame.draw.rect(surface, COLOR_UI_SUCCESS, (px + pw - 40, sy + 24, 28, 22),
                             border_radius=5)
            plus = self.font_lg.render("+", True, (255, 255, 255))
            surface.blit(plus, (px + pw - 30, sy + 24))

    def show_day_summary_panel(self, summary: dict):
        """Activa la pantalla de resumen del día."""
        self.show_day_summary = True
        self.day_summary = summary

    def _draw_day_summary(self, surface):
        """Pantalla de resumen al final del día."""
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        pw, ph = 420, 340
        px = self.sw // 2 - pw // 2
        py = self.sh // 2 - ph // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*COLOR_UI_PANEL, 250))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, COLOR_UI_ACCENT, (px, py, pw, ph), border_radius=12, width=3)

        title = self.font_xl.render(f"✨ Resumen del Día {self.day_summary.get('day', 1)}", True, COLOR_UI_TEXT)
        surface.blit(title, (px + pw // 2 - title.get_width() // 2, py + 16))

        items = [
            ("Ventas del día:",       f"${self.day_summary.get('earned', 0):,.0f}", (60, 140, 60)),
            ("Clientes atendidos:",   str(self.day_summary.get('served', 0)),         COLOR_UI_TEXT),
            ("Clientes que se fueron:",str(self.day_summary.get('left_angry', 0)),    (180, 80, 60)),
            ("Reputación actual:",    f"{self.day_summary.get('reputation', 50):.0f}/100", COLOR_UI_TEXT),
            ("Balance total:",        f"${self.day_summary.get('total', 0):,.0f}",    (60, 100, 180)),
        ]

        for i, (label, value, color) in enumerate(items):
            y = py + 70 + i * 42
            lbl_txt = self.font_lg.render(label, True, COLOR_UI_TEXT)
            val_txt = self.font_lg.render(value, True, color)
            surface.blit(lbl_txt, (px + 20, y))
            surface.blit(val_txt, (px + pw - 20 - val_txt.get_width(), y))
            pygame.draw.line(surface, COLOR_UI_BORDER, (px + 16, y + 36), (px + pw - 16, y + 36), 1)

        self.btn_next_day.rect.centerx = px + pw // 2
        self.btn_next_day.rect.y = py + ph - 58
        self.btn_next_day.draw(surface)
