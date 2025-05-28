import colorsys

import numpy as np
import pygame as pg
from consts import BUG_BASE_SURFACE, TILE_SIZE
from food import Food


class Bug(pg.sprite.DirtySprite):
    turns = ["F", "R", "HR", "RV", "HL", "L"]
    turn_angles = {"F": 0, "R": 60, "HR": 120, "RV": 180, "HL": -120, "L": -60}
    energy_max = 100.0
    food_sustenance = 12
    age_max: int = 300

    energy_min = 60.0
    age_min: int = 130

    mutation_probability = 0.25
    __slots__ = [
        "rect",
        "age",
        "energy",
        "image",
        "position",
        "genes",
        "direction",
        "dirty",
        "blendmode",
        "_visible",
        "move_vector",
        "spatial_grid",
        "food_group",
        "bugs_group",
        "base_color",
        "current_hue_level",
    ]

    def __init__(self, position, food_group, spatial_grid, bugs_group):
        """
        Inicjalizuje nowego buga.

        Args:
            position (pg.Vector2): Początkowa pozycja buga.
            food_group (pg.sprite.Group): Grupa sprite'ów z jedzeniem.
            spatial_grid (SpatialGrid):
            Siatka przestrzenna do zarządzania położeniem.
            bugs_group (pg.sprite.Group): Grupa sprite'ów z innymi bugami.
        """
        super().__init__()
        self.image: pg.Surface = BUG_BASE_SURFACE.copy()
        self.base_color = (0, 255, 0)  # młody = zielony
        self.current_hue_level = None
        self.image.fill(self.base_color)
        self.position: pg.Vector2 = position
        self.rect: pg.Rect = self.image.get_rect(center=self.position)
        self.direction = pg.Vector2(0, -1).normalize()
        self.move_vector = pg.Vector2(0, 0)
        self.food_group = food_group

        self.spatial_grid = spatial_grid
        self.spatial_grid.add(self)

        self.bugs_group = bugs_group
        self.bugs_group.add(self)

        self.genes = {
            "F": 0.0,
            "R": 0.0,
            "HR": 3.0,
            "RV": 2.0,
            "HL": -1.0,
            "L": 3.0,
        }
        self.energy = 50
        self.age = 0

    def update(self):
        if not self.alive():
            return
        self.age_bug()
        self.do_suicide()
        self.eat_food()
        self.move()
        self.multiply()
        self.update_color_by_age()

    def age_bug(self) -> None:
        """Zmniejsza energię buga i zwiększa jego wiek."""
        self.energy = self.energy - 0.25
        self.age = self.age + 1

    def update_color_by_age(self) -> None:
        """Aktualizuje kolor buga na podstawie jego wieku
        (od zielonego do czerwonego)."""
        # Normalizuj wiek (0.0 = młody, 1.0 = stary)
        normalized_age = min(1.0, self.age / self.age_max)

        # Przejście hue: 0.33 (zielony) → 0.0 (czerwony)
        hue_shift = (1 - normalized_age) * 0.33

        if (
            self.current_hue_level is not None
            and abs(hue_shift - self.current_hue_level) < 0.01
        ):
            return

        self.current_hue_level = hue_shift

        # Przekształć RGB na HSV i zmień hue
        r, g, b = self.base_color
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        new_rgb = colorsys.hsv_to_rgb(hue_shift, s, v)
        new_color = tuple(int(c * 255) for c in new_rgb)

        self.image.fill(new_color)

    def move(self):
        """Porusza buga, zmieniając jego kierunek na podstawie genów."""
        gene_str = {k: 2**v for k, v in self.genes.items()}

        # suma sił
        total_str = sum(gene_str.values())

        # prawdopodobieństwo jako P = 2^i / Σ2^i
        probabilities = [gene_str[k] / total_str for k in self.turns]

        # skręt na podstawie prawdopodobieństw
        turn = np.random.choice(a=self.turns, p=probabilities)
        angle = self.turn_angles[turn]

        # obrót kierunku
        rotated_direction = self.direction.rotate(angle)
        self.move_vector = rotated_direction * 2 * TILE_SIZE
        new_position = self.position + self.move_vector

        screen_width, screen_height = pg.display.get_surface().get_size()
        new_position.x = new_position.x % screen_width
        new_position.y = new_position.y % screen_height

        self.position = new_position
        self.rect.center = self.position
        self.direction = rotated_direction.normalize()

        self.dirty = 1
        self.spatial_grid.update(self)

    def eat_food(self):
        """Sprawdza, czy bug może zjeść pobliskie
        jedzenie i jeśli tak, zjada je."""
        if self.energy + self.food_sustenance <= self.energy_max:
            nearby_sprites = self.spatial_grid.get_nearby(self)
            for sprite in nearby_sprites:
                if isinstance(
                    sprite,
                    Food,
                ) and self.rect.colliderect(sprite.rect):
                    self.spatial_grid.remove(sprite)
                    sprite.kill()
                    self.energy += self.food_sustenance
                    break

    def do_suicide(self):
        """Sprawdza, czy bug powinien umrzeć z powodu
        braku energii lub starości i usuwa go."""
        if self.energy <= 0.5 or self.age >= self.age_max:
            self.spatial_grid.remove(self)
            self.kill()

    def multiply(self) -> None:
        """Sprawdza, czy bug może się
        rozmnożyć i jeśli tak, tworzy nowego buga."""
        if self.energy >= self.energy_min and self.age >= self.age_min:
            child = Bug(
                self.position.copy(),
                self.food_group,
                self.spatial_grid,
                self.bugs_group,
            )
            self.energy //= 2
            child.energy = self.energy
            if child.energy != self.energy:
                print(f"CHILD:{child.energy} PARENT:{self.energy}")
            child.genes = self.genes.copy()
            if np.random.random() < self.mutation_probability:
                random_gene = np.random.choice(self.turns)
                child.genes[random_gene] += np.random.choice([-1, 1])
            self.spatial_grid.add(child)
            self.spatial_grid.update(child)
            self.dirty = 1
