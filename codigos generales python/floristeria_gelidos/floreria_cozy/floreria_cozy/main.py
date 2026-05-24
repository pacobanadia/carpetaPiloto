"""
main.py — Punto de entrada principal del juego "Florería Cozy"
==============================================================
Inicializa Pygame, crea la ventana principal y coordina el bucle
de juego. Actúa como director entre todos los módulos.

Arquitectura general:
    main.py ──► GameManager
                    ├── player.py    (Player)
                    ├── customer.py  (CustomerManager)
                    ├── plants.py    (PlantManager)
                    ├── shop.py      (Shop)
                    ├── inventory.py (Inventory)
                    └── ui.py        (UI)
"""

import pygame
import sys
import json
import os
from game_manager import GameManager

# ── Configuración global ──────────────────────────────────────
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE  = "🌸 Florería Cozy"
TARGET_FPS    = 60


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Crear ventana principal
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Ícono de la ventana (flor simple dibujada programáticamente)
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, (255, 182, 193), (16, 16), 12)
    pygame.draw.circle(icon, (255, 255, 100), (16, 16), 5)
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()

    # Inicializar el director del juego
    game = GameManager(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

    # ── Bucle principal ───────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(TARGET_FPS) / 1000.0  # delta time en segundos

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # Actualizar lógica
        game.update(dt)

        # Renderizar
        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()

    # Guardar partida al salir
    game.save_game()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
