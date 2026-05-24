"""
customer.py — IA de clientes y sistema de gestión de clientes
=============================================================
Implementa el comportamiento de los clientes: entran a la tienda,
buscan productos en estantes, hacen fila en la caja y reaccionan
a precios y tiempos de espera.

Clases:
    CustomerState   — Máquina de estados del cliente
    Customer        — Entidad de cliente individual
    CustomerManager — Administra todos los clientes activos
"""

import pygame
import math
import random
from config import (
    CUSTOMER_SPEED, CUSTOMER_PATIENCE, TILE_SIZE,
    CUSTOMER_PALETTES, SHELF_POSITIONS, CASH_REGISTER,
    DOOR_POSITION, FLOWER_SELL_PRICES,
)


class CustomerState:
    ENTERING    = "entering"    # Caminando hacia la tienda
    BROWSING    = "browsing"    # Buscando un estante
    MOVING      = "moving"      # En tránsito a objetivo
    AT_SHELF    = "at_shelf"    # Evaluando producto en estante
    QUEUING     = "queuing"     # En fila hacia la caja
    WAITING     = "waiting"     # Esperando ser atendido en caja
    LEAVING_OK  = "leaving_ok"  # Saliendo satisfecho
    LEAVING_MAD = "leaving_mad" # Saliendo molesto


class Customer:
    """
    Cliente con IA sencilla y funcional.
    Parámetros de comportamiento generados aleatoriamente por cliente.
    """

    SIZE = 14  # Radio visual

    def __init__(self, spawn_x: float, spawn_y: float, cid: int):
        self.id  = cid
        self.x   = float(spawn_x)
        self.y   = float(spawn_y)

        # Paleta visual aleatoria
        palette = random.choice(CUSTOMER_PALETTES)
        self.body_color  = palette["body"]
        self.shirt_color = palette["shirt"]
        self.hair_color  = palette["hair"]

        # Parámetros de personalidad
        self.patience_max = CUSTOMER_PATIENCE + random.uniform(-10, 15)
        self.patience     = self.patience_max
        self.budget       = random.uniform(20, 120)   # Cuánto quiere gastar
        self.price_sensitivity = random.uniform(0.5, 1.5)  # 1.0 = neutral

        # Flor deseada (puede ser None = cualquiera disponible)
        all_types = list(FLOWER_SELL_PRICES.keys())
        self.desired_flower = random.choice(all_types) if random.random() > 0.3 else None
        self.items_bought: list[str] = []
        self.total_spent   = 0.0

        # Estado de IA
        self.state  = CustomerState.ENTERING
        self.target_x: float = 0
        self.target_y: float = 0
        self._target_shelf_pos: tuple | None = None
        self._browse_timer  = 0.0   # Tiempo evaluando un estante
        self._think_timer   = 0.0   # Pausa antes de decidir

        # Animación
        self._walk_cycle = random.uniform(0, 2 * math.pi)
        self._happy_bounce = 0.0
        self._mad_shake    = 0.0

        # Referencia a estante asignado (para evitar que dos clientes vayan al mismo)
        self.assigned_shelf = None

        # Posición en la fila de caja
        self.queue_position = 0

        # Efectos visuales de salida
        self._leaving_timer = 0.0
        self.done = False   # Marcar para eliminar

    # ── IA de comportamiento ──────────────────────────────────

    def update(self, dt: float, shop) -> float:
        """
        Actualiza la IA del cliente. Retorna dinero ganado este frame
        (0 normalmente, positivo al pagar en caja).
        """
        earned = 0.0
        self.patience -= dt

        # El cliente se va furioso si se acaba la paciencia
        if self.patience <= 0 and self.state not in (
                CustomerState.LEAVING_OK, CustomerState.LEAVING_MAD):
            self._start_leaving(angry=True)

        # Máquina de estados
        if self.state == CustomerState.ENTERING:
            earned = self._update_entering(dt, shop)
        elif self.state == CustomerState.BROWSING:
            earned = self._update_browsing(dt, shop)
        elif self.state == CustomerState.MOVING:
            earned = self._update_moving(dt, shop)
        elif self.state == CustomerState.AT_SHELF:
            earned = self._update_at_shelf(dt, shop)
        elif self.state == CustomerState.QUEUING:
            earned = self._update_queuing(dt, shop)
        elif self.state == CustomerState.WAITING:
            earned = self._update_waiting(dt, shop)
        elif self.state in (CustomerState.LEAVING_OK, CustomerState.LEAVING_MAD):
            earned = self._update_leaving(dt, shop)

        # Animaciones de estado especial
        if self.state == CustomerState.LEAVING_OK:
            self._happy_bounce = math.sin(self._walk_cycle * 4) * 3
        elif self.state == CustomerState.LEAVING_MAD:
            self._mad_shake = math.sin(self._walk_cycle * 12) * 3
        else:
            self._happy_bounce *= 0.9
            self._mad_shake    *= 0.9

        return earned

    def _update_entering(self, dt, shop):
        """Entra a la tienda y pasa a explorar."""
        # Destino: área interior de la tienda
        dest_x = 12 * TILE_SIZE + TILE_SIZE // 2
        dest_y = 11 * TILE_SIZE + TILE_SIZE // 2
        if self._move_toward(dest_x, dest_y, dt):
            self.state = CustomerState.BROWSING
            self._think_timer = random.uniform(0.5, 1.5)
        return 0.0

    def _update_browsing(self, dt, shop):
        """Busca un estante con el producto deseado."""
        self._think_timer -= dt
        if self._think_timer > 0:
            return 0.0

        # Buscar estante disponible con flores
        shelf = shop.find_shelf_for_customer(self)
        if shelf is None:
            # No hay nada disponible → irse (triste pero no furioso)
            if not self.items_bought:
                self._start_leaving(angry=False)
            else:
                self._go_to_checkout(shop)
            return 0.0

        self.assigned_shelf = shelf
        self._target_shelf_pos = (shelf.col, shelf.row)
        tx = shelf.col * TILE_SIZE + TILE_SIZE // 2
        ty = shelf.row * TILE_SIZE + TILE_SIZE // 2
        self.target_x = tx
        self.target_y = ty
        self.state = CustomerState.MOVING
        return 0.0

    def _update_moving(self, dt, shop):
        """Se mueve hacia el objetivo actual."""
        arrived = self._move_toward(self.target_x, self.target_y, dt)
        if arrived:
            if self._target_shelf_pos:
                self.state = CustomerState.AT_SHELF
                self._browse_timer = random.uniform(1.5, 3.0)
            else:
                self.state = CustomerState.QUEUING
        return 0.0

    def _update_at_shelf(self, dt, shop):
        """Evalúa el producto y decide si comprar."""
        self._browse_timer -= dt
        if self._browse_timer > 0:
            return 0.0

        shelf = self.assigned_shelf
        if shelf is None or shelf.is_empty:
            self.assigned_shelf = None
            self._target_shelf_pos = None
            self.state = CustomerState.BROWSING
            self._think_timer = 0.5
            return 0.0

        # Evaluar precio (sensibilidad al precio)
        base_price = FLOWER_SELL_PRICES.get(shelf.flower_type, 20.0)
        price_ratio = shelf.price / (base_price * self.price_sensitivity)

        # Probabilidad de comprar según precio
        buy_prob = 1.0 - max(0, (price_ratio - 1.0)) * 0.5
        buy_prob = max(0.1, min(1.0, buy_prob))

        if random.random() < buy_prob and shelf.price <= self.budget:
            # ¡Compra!
            taken = shelf.take_flower()
            if taken:
                self.items_bought.append(taken)
                self.total_spent += shelf.price
                self.budget      -= shelf.price

        self.assigned_shelf    = None
        self._target_shelf_pos = None

        # Seguir comprando o ir a caja
        if self.budget > 10 and random.random() > 0.4:
            self.state        = CustomerState.BROWSING
            self._think_timer = random.uniform(0.3, 1.0)
        else:
            self._go_to_checkout(shop)
        return 0.0

    def _go_to_checkout(self, shop):
        """Dirige al cliente hacia la caja."""
        self.state = CustomerState.QUEUING
        pos = shop.get_queue_position(self)
        self.queue_position = pos
        cx = CASH_REGISTER[0] * TILE_SIZE + TILE_SIZE // 2
        cy = (CASH_REGISTER[1] + pos) * TILE_SIZE + TILE_SIZE // 2
        self.target_x = cx
        self.target_y = cy + pos * TILE_SIZE

    def _update_queuing(self, dt, shop):
        """Camina hacia la posición en la fila."""
        cx = CASH_REGISTER[0] * TILE_SIZE + TILE_SIZE // 2
        cy = (CASH_REGISTER[1] + self.queue_position + 1) * TILE_SIZE
        if self._move_toward(cx, cy, dt):
            self.state = CustomerState.WAITING
        return 0.0

    def _update_waiting(self, dt, shop):
        """Espera a ser atendido. La paciencia ya descuenta globalmente."""
        return 0.0

    def checkout(self) -> float:
        """Llamado por el jugador. Procesa el pago y marca al cliente para salir."""
        total = self.total_spent
        self._start_leaving(angry=False)
        return total

    def _update_leaving(self, dt, shop):
        """Camina hacia la salida y se elimina."""
        dx = DOOR_POSITION[0] * TILE_SIZE + TILE_SIZE // 2
        dy = DOOR_POSITION[1] * TILE_SIZE + TILE_SIZE // 2
        if self._move_toward(dx, dy, dt):
            self.done = True
        return 0.0

    def _start_leaving(self, angry: bool):
        self.state = CustomerState.LEAVING_MAD if angry else CustomerState.LEAVING_OK
        if self.assigned_shelf:
            self.assigned_shelf = None

    def _move_toward(self, tx: float, ty: float, dt: float) -> bool:
        """Mueve el cliente hacia (tx, ty). Retorna True si llegó."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 4:
            self.x = tx
            self.y = ty
            return True
        speed = CUSTOMER_SPEED * dt
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed
        self._walk_cycle += dt * 7.0
        return False

    # ── Dibujo ────────────────────────────────────────────────

    def draw(self, surface, camera_x: int, camera_y: int):
        sx = int(self.x - camera_x + self._mad_shake)
        sy = int(self.y - camera_y - self._happy_bounce)

        leg_swing = math.sin(self._walk_cycle) * 4

        # Sombra
        shadow = pygame.Surface((24, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (0, 0, 24, 8))
        surface.blit(shadow, (sx - 12, sy + 7))

        # Piernas
        pygame.draw.rect(surface, (80, 60, 40),
                         (sx - 5, sy + 3 - int(leg_swing), 4, 8))
        pygame.draw.rect(surface, (80, 60, 40),
                         (sx + 1, sy + 3 + int(leg_swing), 4, 8))

        # Cuerpo
        pygame.draw.rect(surface, self.shirt_color,
                         (sx - 7, sy - 7, 14, 12), border_radius=3)

        # Brazos
        arm = math.sin(self._walk_cycle) * 3
        pygame.draw.rect(surface, self.shirt_color,
                         (sx - 11, sy - 5 + int(arm), 4, 7), border_radius=2)
        pygame.draw.rect(surface, self.shirt_color,
                         (sx + 7, sy - 5 - int(arm), 4, 7), border_radius=2)

        # Cabeza
        pygame.draw.circle(surface, self.body_color, (sx, sy - 13), 9)
        pygame.draw.arc(surface, self.hair_color,
                        (sx - 9, sy - 22, 18, 16), 0, math.pi, 4)

        # Ojos
        pygame.draw.circle(surface, (50, 30, 10), (sx - 3, sy - 14), 2)
        pygame.draw.circle(surface, (50, 30, 10), (sx + 3, sy - 14), 2)

        # Expresión según estado
        if self.state == CustomerState.LEAVING_MAD:
            # Cejas fruncidas
            pygame.draw.line(surface, (80, 40, 20),
                             (sx - 6, sy - 17), (sx - 2, sy - 16), 2)
            pygame.draw.line(surface, (80, 40, 20),
                             (sx + 2, sy - 16), (sx + 6, sy - 17), 2)
        elif self.state == CustomerState.LEAVING_OK:
            # Sonrisa
            pygame.draw.arc(surface, (180, 80, 60),
                            (sx - 4, sy - 11, 8, 5), math.pi, 2 * math.pi, 2)

        # Barra de paciencia (solo si está esperando)
        if self.state == CustomerState.WAITING:
            _draw_patience_bar(surface, sx, sy - 26, self.patience / self.patience_max)

        # Bolsa de compras si lleva items
        if self.items_bought:
            pygame.draw.rect(surface, (200, 180, 140),
                             (sx + 8, sy - 3, 8, 10), border_radius=2)
            pygame.draw.line(surface, (160, 130, 90),
                             (sx + 9, sy - 3), (sx + 9, sy - 7), 1)
            pygame.draw.line(surface, (160, 130, 90),
                             (sx + 14, sy - 3), (sx + 14, sy - 7), 1)


def _draw_patience_bar(surface, cx, cy, ratio):
    w = 22
    h = 4
    pygame.draw.rect(surface, (200, 100, 100), (cx - w // 2, cy, w, h), border_radius=2)
    color = (90, 200, 90) if ratio > 0.5 else (220, 180, 50) if ratio > 0.25 else (220, 60, 60)
    pygame.draw.rect(surface, color,
                     (cx - w // 2, cy, int(w * ratio), h), border_radius=2)


class CustomerManager:
    """
    Controla la generación y ciclo de vida de todos los clientes.
    """

    def __init__(self):
        self.customers: list[Customer] = []
        self._spawn_timer = 10.0    # Primer cliente llega pronto
        self._spawn_interval = 18.0
        self._next_id = 0
        self.queue: list[Customer] = []  # Clientes esperando en caja

    def update(self, dt: float, shop, store_open: bool) -> tuple[float, int, int]:
        """
        Actualiza todos los clientes.
        Retorna (dinero_ganado, clientes_satisfechos, clientes_molestos).
        """
        earned = 0.0
        happy  = 0
        mad    = 0

        if store_open:
            self._spawn_timer -= dt
            if self._spawn_timer <= 0:
                self._spawn_customer()
                self._spawn_timer = self._spawn_interval

        for customer in self.customers:
            earned += customer.update(dt, shop)

        # Actualizar fila
        self.queue = [c for c in self.customers
                      if c.state == CustomerState.WAITING]
        for i, c in enumerate(self.queue):
            c.queue_position = i

        # Eliminar clientes que ya salieron
        for c in self.customers:
            if c.done:
                if c.state == CustomerState.LEAVING_OK:
                    happy += 1
                else:
                    mad += 1

        self.customers = [c for c in self.customers if not c.done]
        return earned, happy, mad

    def checkout_next(self) -> Customer | None:
        """Retorna el primer cliente en la fila (posición 0) listo para cobrar."""
        if self.queue:
            return self.queue[0]
        return None

    def _spawn_customer(self):
        # Genera desde la puerta
        sx = DOOR_POSITION[0] * TILE_SIZE + TILE_SIZE // 2
        sy = (DOOR_POSITION[1] + 1) * TILE_SIZE
        c = Customer(sx, sy, self._next_id)
        self._next_id += 1
        self.customers.append(c)

    def draw(self, surface, camera_x: int, camera_y: int):
        for customer in self.customers:
            customer.draw(surface, camera_x, camera_y)

    def draw_queue_indicator(self, surface, camera_x: int, camera_y: int):
        """Dibuja un indicador sobre el primer cliente en espera."""
        if self.queue:
            c = self.queue[0]
            sx = int(c.x - camera_x)
            sy = int(c.y - camera_y) - 32
            # Flecha parpadeante
            import time
            alpha = int(180 + 75 * math.sin(time.time() * 4))
            arrow = pygame.Surface((16, 16), pygame.SRCALPHA)
            points = [(8, 0), (16, 10), (11, 10), (11, 16), (5, 16), (5, 10), (0, 10)]
            pygame.draw.polygon(arrow, (255, 200, 50, alpha), points)
            surface.blit(arrow, (sx - 8, sy))
