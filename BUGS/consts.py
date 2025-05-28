import pygame as pg

TILE_SIZE = 2

# === Optymalizacja Surface dla Bug ===
BUG_BASE_SURFACE = pg.Surface((TILE_SIZE * 3 - 1, TILE_SIZE * 3 - 1))
BUG_BASE_SURFACE.fill((0, 255, 0))

# === Optymalizacja Surface dla Food ===
FOOD_BASE_SURFACE = pg.Surface((TILE_SIZE - 1, TILE_SIZE - 1))
FOOD_BASE_SURFACE.fill(pg.Color("red"))
