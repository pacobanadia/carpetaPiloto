"""
inventory.py — Sistema de inventario del jugador
================================================
Gestiona las flores cosechadas que el jugador lleva consigo,
el stock en exhibición de la tienda y las transacciones de compra.

Clases:
    Inventory — Mochila/bolsa del jugador
    ShelfSlot — Ranura individual en un estante de exhibición
"""

from config import FLOWER_SELL_PRICES, SEED_PRICES


class Inventory:
    """
    Inventario portátil del jugador. Almacena flores cosechadas
    listas para colocar en estantes o vender directamente.
    """

    def __init__(self):
        # Diccionario {tipo_flor: cantidad}
        self.flowers: dict[str, int] = {}
        # Semillas disponibles para plantar
        self.seeds: dict[str, int] = {}
        # Capacidad máxima de flores
        self.capacity = 20

    # ── Flores ────────────────────────────────────────────────

    def add_flower(self, flower_type: str, amount: int = 1) -> bool:
        """Intenta agregar flores al inventario. Retorna False si está lleno."""
        total = sum(self.flowers.values())
        if total + amount > self.capacity:
            return False
        self.flowers[flower_type] = self.flowers.get(flower_type, 0) + amount
        return True

    def remove_flower(self, flower_type: str, amount: int = 1) -> bool:
        """Elimina flores del inventario. Retorna False si no hay suficientes."""
        current = self.flowers.get(flower_type, 0)
        if current < amount:
            return False
        self.flowers[flower_type] = current - amount
        if self.flowers[flower_type] == 0:
            del self.flowers[flower_type]
        return True

    def total_flowers(self) -> int:
        return sum(self.flowers.values())

    def is_full(self) -> bool:
        return self.total_flowers() >= self.capacity

    # ── Semillas ──────────────────────────────────────────────

    def add_seeds(self, flower_type: str, amount: int = 1):
        self.seeds[flower_type] = self.seeds.get(flower_type, 0) + amount

    def use_seed(self, flower_type: str) -> bool:
        """Consume una semilla para plantarla. Retorna False si no hay."""
        if self.seeds.get(flower_type, 0) <= 0:
            return False
        self.seeds[flower_type] -= 1
        if self.seeds[flower_type] == 0:
            del self.seeds[flower_type]
        return True

    # ── Serialización ─────────────────────────────────────────

    def to_dict(self) -> dict:
        return {"flowers": self.flowers.copy(), "seeds": self.seeds.copy()}

    def from_dict(self, data: dict):
        self.flowers = data.get("flowers", {})
        self.seeds   = data.get("seeds", {})


class ShelfSlot:
    """
    Ranura de exhibición en la tienda. Puede contener flores de un
    tipo determinado con un stock máximo y un precio configurable.
    """

    MAX_STOCK = 5  # flores por ranura

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.flower_type: str | None = None
        self.stock: int = 0
        # El precio se inicializa al precio base de venta
        self.price: float = 0.0

    @property
    def is_empty(self) -> bool:
        return self.stock == 0

    @property
    def is_full(self) -> bool:
        return self.stock >= self.MAX_STOCK

    def stock_flower(self, flower_type: str) -> bool:
        """
        Coloca una flor en la ranura. Si ya tiene otro tipo, falla.
        Si tiene el mismo tipo y hay espacio, incrementa stock.
        """
        if self.flower_type is not None and self.flower_type != flower_type:
            return False  # Ranura ocupada por otro tipo
        if self.is_full:
            return False
        self.flower_type = flower_type
        self.stock += 1
        if self.price == 0.0:
            # Precio predeterminado al base de venta
            self.price = FLOWER_SELL_PRICES.get(flower_type, 20.0)
        return True

    def take_flower(self) -> str | None:
        """Un cliente toma una flor. Retorna el tipo o None si vacía."""
        if self.stock <= 0:
            return None
        self.stock -= 1
        taken = self.flower_type
        if self.stock == 0:
            self.flower_type = None
        return taken

    def to_dict(self) -> dict:
        return {
            "col": self.col, "row": self.row,
            "flower_type": self.flower_type,
            "stock": self.stock, "price": self.price
        }

    def from_dict(self, data: dict):
        self.flower_type = data.get("flower_type")
        self.stock       = data.get("stock", 0)
        self.price       = data.get("price", 0.0)
