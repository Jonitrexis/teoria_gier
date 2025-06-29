import numpy as np
import pygame as pg
from consts import TILE_SIZE, PREDATOR_MAX_AGE, PREDATOR_MAX_ENERGY
from creature import Creature
from smell_map import SmellMap


class Predator(Creature):
    bug_sustenance = 35

    __slots__ = Creature.__slots__ + [
        "bugs_group",
        "predators_group",
        "smell_map",
    ]

    def __init__(
        self,
        position,
        spatial_grid,
        bugs_group,
        predators_group,
        smell_map,
    ):
        """
        Inicjalizuje nowego predatora.

        Args:
            position (pg.Vector2): Początkowa pozycja predatora.
            spatial_grid (SpatialGrid):
            Siatka przestrzenna do zarządzania położeniem.
            bugs_group (pg.sprite.Group): Grupa sprite'ów z bugami.
            predators_group (pg.sprite.Group): Grupa sprite'ów z predatorami.
            smell_map (SmellMap): Mapa zapachu rozprzestrzenianego dyfuzją.

        """
        super().__init__(
            position,
            spatial_grid,
            base_color=(0, 0, 255),
            energy_max=PREDATOR_MAX_ENERGY,
            age_max=PREDATOR_MAX_AGE,
        )

        self.bugs_group = bugs_group

        self.predators_group = predators_group
        self.predators_group.add(self)

        self.smell_map: SmellMap = smell_map

        (
            self.screen_width,
            self.screen_height,
        ) = pg.display.get_surface().get_size()

    def update(self):
        if not self.alive():
            return
        self.age_creature()
        self.do_suicide()
        self.eat_bug()
        self.move()
        self.multiply()

    def move(self):
        """Porusza predatora, zmieniając jego kierunek na podstawie zapachu."""

        best_smell, best_turn = -1.0, None
        gx = int(self.position.x // TILE_SIZE)
        gy = int(self.position.y // TILE_SIZE)
        grid = self.smell_map.grid

        for turn in self.turns:
            vec = self.direction.rotate(self.turn_angles[turn])
            coords = [
                (gx + int(vec.x), gy + int(vec.y)),
                (
                    gx + int(self.direction.rotate(self.turn_angles[turn] + 30).x),
                    gy + int(self.direction.rotate(self.turn_angles[turn] + 30).y),
                ),
                (
                    gx + int(self.direction.rotate(self.turn_angles[turn] - 30).x),
                    gy + int(self.direction.rotate(self.turn_angles[turn] - 30).y),
                ),
            ]
            smell = sum(
                grid[y][x]
                for x, y in coords
                if 0 <= x < grid.shape[1] and 0 <= y < grid.shape[0]
            )
            if smell > best_smell:
                best_smell, best_turn = smell, turn

        nearby = self.spatial_grid.get_nearby(self)
        num_neighbors = sum(1 for s in nearby if s in self.predators_group)

        if num_neighbors > 3:
            # Jest zbyt tłoczno — losowo zmień kierunek, by się rozproszyć
            angle = self.turn_angles[np.random.choice(self.turns)]
            new_dir = self.direction.rotate(angle)
            self.move_forward(new_dir)
            return

        if best_smell <= 0:
            # Szukamy losowego ruchu prowadzącego do wolnej przestrzeni
            for _ in range(6):
                turn = np.random.choice(self.turns)
                angle = self.turn_angles[turn]
                new_dir = self.direction.rotate(angle)
                new_pos = self.position + new_dir
                if (
                    0 <= new_pos.x < self.screen_width // TILE_SIZE
                    and 0 <= new_pos.y < self.screen_height // TILE_SIZE
                ):
                    self.move_forward(new_dir)
                    return
            # Nie udało się znaleźć dobrego kierunku
            return
        else:
            angle = self.turn_angles[best_turn]
            new_dir = self.direction.rotate(angle)
            self.move_forward(new_dir)

    def eat_bug(self):
        """Sprawdza, czy predator może zjeść pobliskiego buga
        i jeśli tak, zjada go."""
        if self.energy + self.bug_sustenance > self.energy_max:
            return

        nearby = self.spatial_grid.get_nearby(self)
        # znajdujemy tylko pierwszego buga, który się z nami zderza
        nearby_bugs = [s for s in nearby if s in self.bugs_group]
        target = next(
            (s for s in nearby_bugs if self.rect.colliderect(s.rect)),
            None,
        )
        if target:
            self.spatial_grid.remove(target)
            target.kill()
            self.energy += self.bug_sustenance
            gx = int(target.position.x // TILE_SIZE)
            gy = int(target.position.y // TILE_SIZE)

            if (
                0 <= gx < self.smell_map.grid.shape[1]
                and 0 <= gy < self.smell_map.grid.shape[0]
            ):
                self.smell_map.grid[gy][gx] = 0

    def multiply(self) -> None:
        """Sprawdza, czy predator może się
        rozmnożyć i jeśli tak, tworzy nowego predatora."""
        if self.energy >= self.energy_min and self.age >= self.age_min:
            child = Predator(
                self.position.copy(),
                self.spatial_grid,
                self.bugs_group,
                self.predators_group,
                self.smell_map,
            )
            self.energy //= 2
            child.energy = self.energy
            self.spatial_grid.add(child)
            self.spatial_grid.update(child)
            self.dirty = 1
