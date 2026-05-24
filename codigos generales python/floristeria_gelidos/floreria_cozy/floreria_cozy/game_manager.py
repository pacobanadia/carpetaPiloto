"""
game_manager.py — Director central del juego
=============================================
Coordina todos los módulos: player, customers, plants, shop, ui.
Gestiona el bucle de juego completo: input → update → draw.
También maneja el guardado/carga de partida, el ciclo día/noche,
la economía y el sistema de reputación.
"""

import pygame
import math
import json
import os
import time
from config import (
    STARTING_MONEY, PLAYER_START, TILE_SIZE, DAY_DURATION,
    CHECKOUT_TIME, REPUTATION_GAIN_SALE, REPUTATION_LOSS_LEAVE,
    MAX_REPUTATION, SEED_PRICES, CASH_REGISTER, GARDEN_AREA,
    WINDOW_WIDTH, WINDOW_HEIGHT, SAVE_FILE,
)
from player   import Player, PlayerState
from customer import CustomerManager, CustomerState
from plants   import PlantManager, PlantStage
from shop     import Shop
from inventory import Inventory
from ui       import UI


class GameManager:
    """
    Director central. Posee referencias a todos los subsistemas e
    implementa la lógica de alto nivel:
    - Ciclo día/noche y apertura/cierre de tienda
    - Economía (ingresos, gastos, reputación)
    - Interacciones del jugador (plantar, cosechar, reabastecer, cobrar)
    - Serialización de estado (guardado/carga JSON)
    """

    def __init__(self, screen: pygame.Surface, sw: int, sh: int):
        self.screen = screen
        self.sw = sw
        self.sh = sh

        # ── Subsistemas ───────────────────────────────────────
        self.shop     = Shop()
        self.inventory= Inventory()
        self.plants   = PlantManager()
        self.player   = Player(*PLAYER_START)
        self.customers= CustomerManager()
        self.ui       = UI(sw, sh)

        # ── Economía ──────────────────────────────────────────
        self.money      = STARTING_MONEY
        self.day        = 1
        self.reputation = 50.0

        # ── Ciclo temporal ────────────────────────────────────
        self.time_of_day   = 0.0   # 0 .. DAY_DURATION (segundos)
        self.store_open    = True
        self._day_earned   = 0.0
        self._day_served   = 0
        self._day_left_mad = 0

        # Tiempo total transcurrido (para animaciones)
        self._time_elapsed = 0.0

        # ── Cámara ────────────────────────────────────────────
        # La cámara centra al jugador en pantalla
        self.cam_x = 0
        self.cam_y = 0

        # ── Checkout ──────────────────────────────────────────
        self._checkout_timer = 0.0
        self._processing_checkout = False

        # ── Efectos de iluminación día/noche ──────────────────
        self._overlay_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        # Intentar cargar partida guardada
        self.load_game()

    # ── Bucle principal ───────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        """Distribuye eventos a los subsistemas correspondientes."""
        gs = self._build_game_state()
        actions = self.ui.handle_event(event, gs)

        # Procesar acciones de UI
        if actions.get("buy_seed"):
            self._buy_seed(actions["buy_seed"], actions.get("seed_price", 0))
        if actions.get("next_day"):
            self._start_next_day()
        if "price_change" in actions:
            idx, delta = actions["price_change"]
            self._adjust_price(idx, delta)

        # Reabastecer estante (click en estante cercano con flores en inv)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not (self.ui.show_seed_shop or self.ui.show_inventory or
                    self.ui.show_price_panel or self.ui.show_day_summary):
                self._handle_world_click(event.pos)

    def update(self, dt: float):
        """Actualiza toda la lógica del juego."""
        self._time_elapsed += dt

        # ── Ciclo de día ──────────────────────────────────────
        self.time_of_day += dt
        if self.time_of_day >= DAY_DURATION:
            self._end_day()
            return

        # Determinar si la tienda está abierta según la hora del día
        hour = 8 + (self.time_of_day / DAY_DURATION) * 12
        self.store_open = True  # Siempre abierta durante el día

        # ── Movimiento del jugador ────────────────────────────
        keys = pygame.key.get_pressed()
        if not self.ui.show_day_summary:
            self.player.handle_input(keys, dt, self.shop.is_walkable)
        self.player.update(dt)

        # ── Plantas ───────────────────────────────────────────
        self.plants.update(dt, self._time_elapsed)

        # ── Clientes ──────────────────────────────────────────
        # Pasar la lista de clientes al shop para asignación de estantes
        self.shop._customer_list = self.customers.customers
        earned, happy, mad = self.customers.update(dt, self.shop, self.store_open)

        if earned > 0:
            self.money        += earned
            self._day_earned  += earned
            self._day_served  += happy

        if mad > 0:
            self._day_left_mad += mad
            self.reputation    = max(0, self.reputation - REPUTATION_LOSS_LEAVE * mad)
            self.ui.notify(f"😠 Cliente molesto salió!", color=(200, 80, 60))

        # ── Checkout automático de acción ─────────────────────
        if self._processing_checkout:
            self._checkout_timer -= dt
            if self._checkout_timer <= 0:
                self._complete_checkout()

        # ── Cámara suave (lerp hacia el jugador) ──────────────
        target_cam_x = int(self.player.x - self.sw // 2)
        target_cam_y = int(self.player.y - self.sh // 2)
        # Clampear para no salir del mapa
        from config import MAP_COLS, MAP_ROWS
        max_cam_x = MAP_COLS * TILE_SIZE - self.sw
        max_cam_y = MAP_ROWS * TILE_SIZE - self.sh
        target_cam_x = max(0, min(target_cam_x, max_cam_x))
        target_cam_y = max(0, min(target_cam_y, max_cam_y))
        # Interpolación suave
        self.cam_x += int((target_cam_x - self.cam_x) * min(dt * 8, 1))
        self.cam_y += int((target_cam_y - self.cam_y) * min(dt * 8, 1))

        # ── Interacciones automáticas por cercanía ────────────
        if not self.ui.show_day_summary:
            self._check_proximity_actions(keys)

        # ── UI ────────────────────────────────────────────────
        self.ui.update(dt)

    def draw(self, surface: pygame.Surface):
        """Renderiza el frame completo."""
        # Fondo (cielo/exterior)
        surface.fill((168, 218, 255))

        # Mundo: tiles, plantas, clientes, jugador
        self.shop.draw(surface, self.cam_x, self.cam_y, self._time_elapsed)
        self.plants.draw(surface, self.cam_x, self.cam_y, self._time_elapsed)
        self.customers.draw(surface, self.cam_x, self.cam_y)
        self.customers.draw_queue_indicator(surface, self.cam_x, self.cam_y)
        self.player.draw(surface, self.cam_x, self.cam_y)

        # Overlay de noche (suave)
        self._draw_day_night_overlay(surface)

        # HUD y UI
        self.ui.draw(surface, self._build_game_state())

    # ── Interacciones ─────────────────────────────────────────

    def _check_proximity_actions(self, keys):
        """Detecta interacciones por teclado según posición del jugador."""
        pcol = self.player.col
        prow = self.player.row

        hints = []

        # Caja registradora
        if self.shop.is_near_cash_register(pcol, prow):
            queue = self.customers.queue
            if queue and not self._processing_checkout:
                hints.append("[E] Cobrar cliente")
                if keys[pygame.K_e] and self.player.state == PlayerState.IDLE:
                    self._start_checkout()

        # Estante cercano (reabastecer)
        nearby_shelf = self._get_nearby_shelf(pcol, prow)
        if nearby_shelf and self.inventory.total_flowers() > 0:
            hints.append("[F] Reabastecer estante")
            if keys[pygame.K_f] and self.player.state == PlayerState.IDLE:
                self._stock_shelf(nearby_shelf)

        # Jardín (plantar o cosechar)
        nearby_plant = self._get_nearby_plant(pcol, prow)
        if nearby_plant:
            if nearby_plant.stage == PlantStage.EMPTY and self.inventory.seeds:
                hints.append("[G] Plantar semilla")
                if keys[pygame.K_g] and self.player.state == PlayerState.IDLE:
                    self._plant_seed(nearby_plant)
            elif nearby_plant.stage == PlantStage.READY:
                hints.append("[G] Cosechar flor")
                if keys[pygame.K_g] and self.player.state == PlayerState.IDLE:
                    self._harvest_plant(nearby_plant)

        # Guardar pistas en el estado del juego para que UI las muestre
        self._current_hints = hints

    def _handle_world_click(self, mouse_pos):
        """Click izquierdo en el mundo: seleccionar estante para reabastecer."""
        wx = mouse_pos[0] + self.cam_x
        wy = mouse_pos[1] + self.cam_y
        col = int(wx // TILE_SIZE)
        row = int(wy // TILE_SIZE)

        # Click en estante
        shelf = self.shop.get_shelf_at(col, row)
        if shelf and self.inventory.total_flowers() > 0:
            dist = self.player.distance_to(col, row)
            if dist < TILE_SIZE * 2.5:
                self._stock_shelf(shelf)
                return

        # Click en maceta de jardín
        plant = self.plants.get_plant_at(col, row)
        if plant:
            dist = self.player.distance_to(col, row)
            if dist < TILE_SIZE * 2.5:
                if plant.stage == PlantStage.EMPTY and self.inventory.seeds:
                    self._plant_seed(plant)
                elif plant.stage == PlantStage.READY:
                    self._harvest_plant(plant)

    # ── Acciones de juego ─────────────────────────────────────

    def _buy_seed(self, flower_type: str, price: float):
        """Compra una semilla al proveedor."""
        if self.money < price:
            self.ui.notify("💸 Sin fondos suficientes", color=(200, 80, 60))
            return
        self.money -= price
        self.inventory.add_seeds(flower_type, 1)
        self.ui.notify(f"🌱 Semilla de {flower_type.capitalize()} comprada! -${price:.0f}",
                       color=(60, 130, 200))

    def _plant_seed(self, plant):
        """Planta la primera semilla disponible en el inventario."""
        if self.player.state != PlayerState.IDLE:
            return
        # Elegir primera semilla disponible
        for flower_type in self.inventory.seeds:
            if self.inventory.use_seed(flower_type):
                def do_plant(ft=flower_type, p=plant):
                    if p.plant_seed(ft):
                        self.ui.notify(f"🌱 {ft.capitalize()} plantada!",
                                       color=(80, 160, 80))
                self.player.start_action(PlayerState.PLANTING, 1.2,
                                         callback=do_plant, text="Plantando...")
                return

    def _harvest_plant(self, plant):
        """Cosecha una flor madura."""
        if self.player.state != PlayerState.IDLE:
            return
        def do_harvest(p=plant):
            harvested = p.harvest()
            if harvested:
                if self.inventory.add_flower(harvested):
                    self.ui.notify(f"🌸 {harvested.capitalize()} cosechada!",
                                   color=(200, 80, 160))
                else:
                    self.ui.notify("🎒 Inventario lleno!", color=(200, 120, 60))
                    p.plant_seed(harvested)  # Devolver a la maceta

        self.player.start_action(PlayerState.HARVEST, 0.8,
                                  callback=do_harvest, text="Cosechando...")

    def _stock_shelf(self, shelf):
        """Reabastece un estante con flores del inventario del jugador."""
        if self.player.state != PlayerState.IDLE:
            return
        if shelf.is_full:
            self.ui.notify("📦 Estante lleno!", color=(180, 130, 60))
            return

        # Elegir qué flor poner (si el estante tiene tipo, usar ese; si no, el primero)
        flower_to_use = shelf.flower_type
        if flower_to_use is None:
            for ft in self.inventory.flowers:
                if self.inventory.flowers[ft] > 0:
                    flower_to_use = ft
                    break

        if flower_to_use is None or self.inventory.flowers.get(flower_to_use, 0) == 0:
            self.ui.notify("🌸 No tienes esa flor", color=(180, 100, 60))
            return

        def do_stock(ft=flower_to_use, s=shelf):
            if self.inventory.remove_flower(ft):
                if s.stock_flower(ft):
                    self.ui.notify(f"📦 {ft.capitalize()} en estante!",
                                   color=(100, 160, 100))
                else:
                    self.inventory.add_flower(ft)  # Devolver si falla

        self.player.start_action(PlayerState.STOCKING, 0.6,
                                  callback=do_stock, text="Colocando...")

    def _start_checkout(self):
        """Inicia el proceso de cobro del primer cliente en fila."""
        if self._processing_checkout:
            return
        customer = self.customers.checkout_next()
        if not customer:
            return
        self._processing_checkout = True
        self._checkout_timer = CHECKOUT_TIME
        self.player.start_action(PlayerState.CHECKOUT, CHECKOUT_TIME,
                                  text="Cobrando...")

    def _complete_checkout(self):
        """Finaliza el cobro y aplica las ganancias."""
        customer = self.customers.checkout_next()
        if customer:
            total = customer.checkout()
            self.money       += total
            self._day_earned += total
            self._day_served += 1
            self.reputation   = min(MAX_REPUTATION,
                                    self.reputation + REPUTATION_GAIN_SALE)
            if total > 0:
                self.ui.notify(f"💰 +${total:.0f}  ¡Gracias!",
                                color=(60, 150, 60))
            else:
                self.ui.notify("🛒 Cliente sin compras", color=(160, 120, 60))
        self._processing_checkout = False
        self._checkout_timer = 0.0

    def _adjust_price(self, shelf_idx: int, delta: int):
        """Ajusta el precio de un estante en incrementos de $1."""
        if 0 <= shelf_idx < len(self.shop.shelves):
            shelf = self.shop.shelves[shelf_idx]
            shelf.price = max(1.0, shelf.price + delta * 1.0)

    # ── Día/noche ─────────────────────────────────────────────

    def _end_day(self):
        """Cierra el día y muestra el resumen."""
        self.time_of_day = 0.0
        summary = {
            "day":        self.day,
            "earned":     self._day_earned,
            "served":     self._day_served,
            "left_angry": self._day_left_mad,
            "reputation": self.reputation,
            "total":      self.money,
        }
        self.ui.show_day_summary_panel(summary)
        self.save_game()

    def _start_next_day(self):
        """Avanza al siguiente día."""
        self.day          += 1
        self._day_earned   = 0.0
        self._day_served   = 0
        self._day_left_mad = 0
        self.time_of_day   = 0.0
        self.store_open    = True
        # Reiniciar timer de clientes
        self.customers._spawn_timer = 12.0

    def _draw_day_night_overlay(self, surface):
        """Aplica un overlay de color según la hora del día."""
        # Normalizar 0..1 donde 0.5 = mediodía (máx claridad)
        t = self.time_of_day / DAY_DURATION
        if t < 0.15:      # Amanecer
            alpha = int(100 * (1 - t / 0.15))
            color = (20, 10, 60, alpha)
        elif t > 0.85:    # Atardecer
            alpha = int(80 * ((t - 0.85) / 0.15))
            color = (40, 20, 80, alpha)
        else:
            return  # Pleno día, sin overlay

        self._overlay_surf.fill(color)
        surface.blit(self._overlay_surf, (0, 0))

    # ── Utilidades de proximidad ──────────────────────────────

    def _get_nearby_shelf(self, col: int, row: int):
        """Retorna el estante más cercano al jugador si está a rango."""
        for shelf in self.shop.shelves:
            if abs(shelf.col - col) <= 1 and abs(shelf.row - row) <= 1:
                return shelf
        return None

    def _get_nearby_plant(self, col: int, row: int):
        """Retorna la maceta más cercana al jugador si está en el jardín."""
        for plant in self.plants.plants:
            if abs(plant.col - col) <= 1 and abs(plant.row - row) <= 1:
                return plant
        return None

    # ── Estado del juego para la UI ───────────────────────────

    def _build_game_state(self) -> dict:
        """Construye el diccionario de estado que consume la UI."""
        shelves_data = [
            {"col": s.col, "row": s.row,
             "flower_type": s.flower_type,
             "stock": s.stock, "price": s.price}
            for s in self.shop.shelves
        ]
        return {
            "money":        self.money,
            "day":          self.day,
            "time_of_day":  self.time_of_day,
            "store_open":   self.store_open,
            "reputation":   self.reputation,
            "flowers":      self.inventory.flowers.copy(),
            "seeds":        self.inventory.seeds.copy(),
            "inv_capacity": self.inventory.capacity,
            "shelves":      shelves_data,
            "hints":        getattr(self, "_current_hints", []),
        }

    # ── Guardado / Carga ──────────────────────────────────────

    def save_game(self):
        """Serializa el estado completo a JSON."""
        os.makedirs("saves", exist_ok=True)
        data = {
            "money":       self.money,
            "day":         self.day,
            "reputation":  self.reputation,
            "time_of_day": self.time_of_day,
            "inventory":   self.inventory.to_dict(),
            "plants":      self.plants.to_dict(),
            "shelves":     self.shop.to_dict(),
            "player":      self.player.to_dict(),
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[GameManager] Error al guardar: {e}")

    def load_game(self):
        """Carga el estado desde JSON si existe."""
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.money      = data.get("money", STARTING_MONEY)
            self.day        = data.get("day", 1)
            self.reputation = data.get("reputation", 50.0)
            self.time_of_day= data.get("time_of_day", 0.0)
            self.inventory.from_dict(data.get("inventory", {}))
            self.plants.from_dict(data.get("plants", []))
            self.shop.from_dict(data.get("shelves", []))
            self.player.from_dict(data.get("player", {}))
            print("[GameManager] Partida cargada correctamente.")
        except Exception as e:
            print(f"[GameManager] Error al cargar: {e}")
