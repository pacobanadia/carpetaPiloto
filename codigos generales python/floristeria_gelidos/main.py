#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from game import Game

def create_placeholder_assets():
    """Crear assets placeholder si no existen"""
    import pygame
    pygame.init()
    assets_dir = Path("assets/sprites")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Player
    surf = pygame.Surface((32, 32))
    surf.fill((0, 255, 0))
    pygame.image.save(surf, "assets/sprites/player.png")
    
    # Customer
    surf.fill((255, 182, 193))
    pygame.image.save(surf, "assets/sprites/customer.png")
    
    print("✅ Assets creados")

if __name__ == "__main__":
    create_placeholder_assets()
    game = Game()
    game.run()