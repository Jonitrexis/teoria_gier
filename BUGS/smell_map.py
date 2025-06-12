import numpy as np
import pygame as pg
from consts import TILE_SIZE
from scipy.ndimage import convolve


class SmellMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.grid_width = width // TILE_SIZE
        self.grid_height = height // TILE_SIZE

        self.grid = np.zeros(
            (self.grid_height, self.grid_width),
            dtype=np.float32,
        )

        self.kernel = np.array(
            [
                [1 / 16, 1 / 16, 1 / 16],
                [1 / 16, 3 / 8, 1 / 16],
                [1 / 16, 1 / 16, 1 / 16],
            ],
            dtype=np.float32,
        )

    def add_smell_source(self, x, y, amount=1.0):
        """Dodaje zapach w miejscu ofiary."""
        gx, gy = x // TILE_SIZE, y // TILE_SIZE
        if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
            self.grid[gy, gx] += amount

    def diffuse(self):
        """Aktualizuje mapę zapachu według modelu dyfuzji."""
        self.grid = convolve(self.grid, self.kernel, mode="constant", cval=0.0)
        self.grid *= 0.99

    def render(self, surface):
        """Rysuje zapach pozostający za ofiarą na ekranie."""
        smell_surface = pg.Surface((self.grid_width, self.grid_height))
        smell_array = pg.surfarray.pixels3d(smell_surface)

        norm_grid = np.clip(self.grid * 50, 0, 255).astype(np.uint8)
        norm_grid = norm_grid.T

        smell_array[:, :, 0] = norm_grid  # R
        smell_array[:, :, 1] = 10 * norm_grid  # G
        smell_array[:, :, 2] = norm_grid  # B

        del smell_array

        scaled = pg.transform.scale(smell_surface, surface.get_size())
        surface.blit(scaled, (0, 0))
