import pygame as pg
from consts import (
    CREATURE_AGE_GAIN,
    CREATURE_BASE_SURFACE,
    CREATURE_ENERGY_LOSS,
    TILE_SIZE,
)


class Creature(pg.sprite.DirtySprite):
    __slots__ = [
        "rect",
        "age",
        "energy",
        "image",
        "position",
        "direction",
        "dirty",
        "blendmode",
        "_visible",
        "move_vector",
        "spatial_grid",
        "base_color",
        "current_hue_level",
        "energy_max",
        "age_max",
        "energy_min",
        "age_min",
    ]

    def __init__(
        self,
        position,
        spatial_grid,
        base_color,
        energy_max,
        age_max,
        energy=50,
    ):
        super().__init__()
        self.image: pg.Surface = CREATURE_BASE_SURFACE.copy()
        self.base_color = base_color
        self.image.fill(base_color)

        self.position: pg.Vector2 = position
        self.rect: pg.Rect = self.image.get_rect(center=self.position)
        self.direction = pg.Vector2(0, -1).normalize()
        self.move_vector = pg.Vector2(0, 0)

        self.spatial_grid = spatial_grid
        self.spatial_grid.add(self)

        self.energy_max = energy_max
        self.energy_min = energy_max * 0.6
        self.age_max = age_max
        self.age_min = age_max * 0.325

        self.energy = energy
        self.age = 0

        self.turns = ["F", "R", "HR", "RV", "HL", "L"]
        self.turn_angles = {
            "F": 0,
            "R": 60,
            "HR": 120,
            "RV": 180,
            "HL": -120,
            "L": -60,
        }

        self.current_hue_level = None
        self.dirty = 1

        (
            self.screen_width,
            self.screen_height,
        ) = pg.display.get_surface().get_size()

    def age_creature(self):
        """Zmniejsza energię i zwiększa wiek."""
        self.energy -= CREATURE_ENERGY_LOSS
        self.age += CREATURE_AGE_GAIN

    def move_forward(self, direction_vector):
        """Przesuwa stworzenie w podanym kierunku."""
        self.move_vector = direction_vector * 2 * TILE_SIZE
        new_position = self.position + self.move_vector
        new_position.x %= self.screen_width
        new_position.y %= self.screen_height
        self.position = new_position
        self.rect.center = self.position
        self.direction = direction_vector.normalize()
        self.dirty = 1
        self.spatial_grid.update(self)

    def do_suicide(self):
        """Usuwa stworzenie, jeśli zbyt stare lub bez energii."""
        if self.energy <= 0.5 or self.age >= self.age_max:
            self.spatial_grid.remove(self)
            self.kill()
