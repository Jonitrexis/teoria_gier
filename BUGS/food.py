import numpy as np
import pygame as pg
from consts import FOOD_BASE_SURFACE, TILE_SIZE


class Food(pg.sprite.DirtySprite):
    def __init__(self, spatial_grid):
        super().__init__()
        screen = pg.display.get_surface()
        width, height = screen.get_width(), screen.get_height()
        x = (
            round(np.random.randint(0, width) / TILE_SIZE) * TILE_SIZE
            + TILE_SIZE / 2
            + 1
        )
        y = (
            round(np.random.randint(0, height) / TILE_SIZE) * TILE_SIZE
            + TILE_SIZE / 2
            + 1
        )
        self.position = pg.Vector2(x, y)
        self.image = FOOD_BASE_SURFACE.copy()
        self.image.fill(pg.Color("red"))
        self.rect = self.image.get_rect(center=self.position)
        self.spatial_grid = spatial_grid
        self.dirty = 1
        self.visible = 1
        self.spatial_grid.add(self)
