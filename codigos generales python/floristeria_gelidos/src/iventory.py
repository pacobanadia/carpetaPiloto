import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    quantity: int
    price: float

class Inventory:
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.money = 1000.0
        
    def add_item(self, name: str, quantity: int, price: float):
        """Añade ítems al inventario"""
        if name in self.items:
            self.items[name].quantity += quantity
        else:
            self.items[name] = Item(name, quantity, price)
    
    def remove_item(self, name: str, quantity: int) -> bool:
        """Remueve ítems del inventario"""
        if name in self.items and self.items[name].quantity >= quantity:
            self.items[name].quantity -= quantity
            if self.items[name].quantity == 0:
                del self.items[name]
            return True
        return False
    
    def buy_seeds(self, name: str, quantity: int, price_per_unit: float) -> bool:
        """Compra semillas"""
        cost = quantity * price_per_unit
        if self.money >= cost:
            self.money -= cost
            self.add_item(name, quantity, price_per_unit)
            return True
        return False
    
    def get_total_flowers(self) -> int:
        """Total de flores disponibles"""
        total = 0
        for item in self.items.values():
            if 'flor_' in item.name:
                total += item.quantity
        return total
    
    def save(self, filepath: str):
        """Guardar inventario"""
        data = {
            'money': self.money,
            'items': {k: {'name': v.name, 'quantity': v.quantity, 'price': v.price} 
                     for k, v in self.items.items()}
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Cargar inventario"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.money = data.get('money', 1000.0)
            self.items = {}
            for k, v in data.get('items', {}).items():
                self.items[k] = Item(v['name'], v['quantity'], v['price'])
        except FileNotFoundError:
            pass