import colorsys

import numpy as np
from creature import Creature
from consts import FOOD_ENERGY, BUG_MAX_AGE, BUG_MAX_ENERGY


class Bug(Creature):

    mutation_probability = 0.25
    __slots__ = Creature.__slots__ + [
        "genes",
        "food_group",
        "bugs_group",
        "smell_map",
    ]

    def __init__(
        self,
        position,
        food_group,
        spatial_grid,
        bugs_group,
        smell_map,
    ):
        """
        Inicjalizuje nowego buga.

        Args:
            position (pg.Vector2): Początkowa pozycja buga.
            food_group (pg.sprite.Group): Grupa sprite'ów z jedzeniem.
            spatial_grid (SpatialGrid):
            Siatka przestrzenna do zarządzania położeniem.
            bugs_group (pg.sprite.Group): Grupa sprite'ów z innymi bugami.
            smell_map (SmellMap): Mapa zapachu rozprzestrzenianego dyfuzją.
        """
        super().__init__(
            position,
            spatial_grid,
            base_color=(0, 255, 0),
            energy_max=BUG_MAX_ENERGY,
            age_max=BUG_MAX_AGE,
        )
        self.is_bug = True
        self.food_group = food_group

        self.bugs_group = bugs_group
        self.bugs_group.add(self)

        self.smell_map = smell_map

        self.genes = {
            "F": 0.0,
            "R": 0.0,
            "HR": 3.0,
            "RV": 2.0,
            "HL": -1.0,
            "L": 3.0,
        }

    def update(self):
        if not self.alive():
            return
        self.age_creature()
        self.do_suicide()
        self.eat_food()
        self.move()
        self.multiply()
        self.update_color_by_age()
        self.leave_smell()

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
        self.move_forward(rotated_direction)

    def eat_food(self):
        """Sprawdza, czy bug może zjeść pobliskie
        jedzenie i jeśli tak, zjada je."""
        if self.energy + FOOD_ENERGY > self.energy_max:
            return

        nearby = self.spatial_grid.get_nearby(self)
        # znajdujemy tylko pierwsze jedzenie który się z nami zderza
        nearby_food = [s for s in nearby if s in self.food_group]
        target = next(
            (s for s in nearby_food if self.rect.colliderect(s.rect)),
            None,
        )
        if target:
            self.spatial_grid.remove(target)
            target.kill()
            self.energy += FOOD_ENERGY

    def multiply(self) -> None:
        """Sprawdza, czy bug może się
        rozmnożyć i jeśli tak, tworzy nowego buga."""
        if self.energy >= self.energy_min and self.age >= self.age_min:
            child = Bug(
                self.position.copy(),
                self.food_group,
                self.spatial_grid,
                self.bugs_group,
                self.smell_map,
            )
            self.energy //= 2
            child.energy = self.energy
            child.genes = self.genes.copy()
            if np.random.random() < self.mutation_probability:
                random_gene = np.random.choice(self.turns)
                child.genes[random_gene] += np.random.choice([-1, 1])
            self.spatial_grid.add(child)
            self.spatial_grid.update(child)
            self.dirty = 1

    def leave_smell(self):
        """Bug zostawia zapach na swojej aktualnej pozycji."""
        grid_x = int(self.position.x)
        grid_y = int(self.position.y)
        self.smell_map.add_smell_source(grid_x, grid_y, amount=1.0)
