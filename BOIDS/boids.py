import colorsys
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import pygame as pg
from vehicle import Vehicle

if TYPE_CHECKING:
    from predator import Predator


class Boid(Vehicle):

    max_acceleration = 0.1

    normal_max_speed = 2.0
    # kąt obserwacji
    perception = 180
    # promień sąsiedzctwa
    neighborhood_radius = 70
    # waga wyrównania
    alignment_factor = 1
    # waga spójności
    cohesion_factor = 0.1
    # waga rozdzielności
    separation_factor = 1
    # odległośc minimalna
    d_min = 20
    # 0.0 = najedzony, 1.0 = maksymalny głód
    hunger = 0.0
    # to jak szybko boid się głodzi w czasie
    hunger_rate = 0.0008

    max_hunger = 1.0

    food_attraction_factor = 0.5

    food_group: pg.sprite.Group = None
    base_color: Tuple[int, int, int] = (209, 125, 146)
    current_hue_level: Optional[int] = None
    # jak boid jest zmęczony, to się mu prędkość zmienia do 20%
    resting_max_speed: float = normal_max_speed * 0.2
    resting: bool = False

    def __init__(self) -> None:
        super().__init__(
            color=self.base_color,
            max_speed=self.normal_max_speed,
        )
        self.boids: List[Boid] = []
        self.predator: Optional[Predator] = None

    def update(self) -> None:
        self.check_resting_state()
        self.make_boid_hungry()
        self.eat_food()
        super().update(self.get_forces_influence(), self.max_acceleration)

    def check_resting_state(self) -> None:
        if self.hunger > 0.7:
            if not self.resting:
                self.resting = True
                self.max_speed = self.resting_max_speed
            # boid minimalny głód odzyskuje podczas odpoczynku
            self.hunger -= 0.002
            # jednak nie więcej niż minimalna ilość głodu potrzebna do ruszenia
            self.hunger = max(self.hunger, 0.6)
        else:
            if self.resting:
                self.resting = False
                self.max_speed = self.normal_max_speed

    def get_food_influence(self) -> pg.Vector2:
        if self.food_group is None or self.hunger < 0.3:
            return pg.Vector2(0, 0)

        closest_food = min(
            self.food_group,
            key=lambda food: self.position.distance_to(food.rect.center),
            default=None,
        )

        if closest_food:
            direction = pg.Vector2(closest_food.rect.center) - self.position
            if direction.length() > 0:
                direction = direction.normalize()
                influence_strength = self.hunger * self.food_attraction_factor
                return direction * influence_strength

        return pg.Vector2(0, 0)

    def eat_food(self) -> None:
        # jeśli jest jakieś jedzenie i boid jest już w miarę głodny
        if self.food_group is not None and self.hunger > 0.3:
            eaten = pg.sprite.spritecollide(
                sprite=self, group=self.food_group, dokill=True
            )
            if eaten:
                self.hunger = 0.0

    def make_boid_hungry(self) -> None:
        self.hunger = min(self.max_hunger, self.hunger + self.hunger_rate)
        # przelicz głód na hue
        # max 0.9, by nie zawijać do czerwieni
        hue_shift = (1 - self.hunger) * 0.9
        if (
            self.current_hue_level is not None
            and abs(hue_shift - self.current_hue_level) < 0.01
        ):
            # pomiń aktualizację, jeśli zmiana zbyt mała
            return

        self.current_hue_level = hue_shift

        # konwersja RGB -> HSV -> zmiana hue -> RGB
        r, g, b = self.base_color
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        new_rgb = colorsys.hsv_to_rgb(hue_shift, s, v)
        new_color = tuple(int(c * 255) for c in new_rgb)

        # rysowanie trójkąta od nowa
        # przezroczyste tło
        self.original_image.fill((0, 0, 0, 0))
        pg.gfxdraw.filled_polygon(
            self.original_image,
            self.TRIANGLE_POINTS,
            new_color,
        )

        # wyczyść cache, by rotacje miały nowy kolor
        self.angle_cache.clear()

    def get_forces_influence(self) -> pg.Vector2:
        cohesion_force: pg.Vector2 = pg.Vector2(0, 0)
        average_position: pg.Vector2 = pg.Vector2(0, 0)
        neighbors_count: int = 0
        separation_count: int = 0
        alignment_force: pg.Vector2 = pg.Vector2(0, 0)
        average_speed: pg.Vector2 = pg.Vector2(0, 0)
        separation_force: pg.Vector2 = pg.Vector2(0, 0)
        fear_force: pg.Vector2 = pg.Vector2(0, 0)

        cohesion_sum: pg.Vector2 = pg.Vector2(0, 0)
        alignment_sum: pg.Vector2 = pg.Vector2(0, 0)
        separation_sum: pg.Vector2 = pg.Vector2(0, 0)
        # zmieniamy na radiany,
        # bo to przyspiesza pracę (zamiast liczyć np.degrees co iterację)
        cached_angle_rad = np.radians(self.last_rotation_angle)
        perception_half = np.radians(self.perception / 2)
        for boid in self.boids:
            if boid is not self:
                # obliczamy odległość
                distance = self.position.distance_to(boid.position)

                # jeśli boid znajduje się w zasięgu (neighborhood_radius)
                if distance < self.neighborhood_radius:

                    angle_to_boid = np.arctan2(
                        boid.position.y - self.position.y,
                        boid.position.x - self.position.x,
                    )

                    # obliczamy różnicę między kątami (w radianach)
                    angle_diff = np.abs(cached_angle_rad - angle_to_boid)

                    # sprawdzamy różnicę kątów, jeśli jest większa niż 180,
                    #  to zmniejszamy ją
                    if angle_diff > np.pi:
                        angle_diff = 2 * np.pi - angle_diff

                    # jeśli boid znajduje się w zasięgu pola widzenia
                    if angle_diff < perception_half:
                        # cohesion
                        cohesion_sum += boid.position
                        # alignment
                        alignment_sum += boid.velocity
                        neighbors_count += 1

                        # separation
                        if 0 < distance < self.d_min:
                            direction = boid.position - self.position
                            # zastosowanie wzoru na siłę separacji
                            separation_strength = self.separation_factor * (
                                (1 - (self.d_min / abs(distance))) * direction
                            )
                            separation_sum += separation_strength
                            separation_count += 1
        if neighbors_count > 0:
            average_position = cohesion_sum / neighbors_count
            cohesion_force = self.cohesion_factor * (average_position - self.position)

            average_speed = alignment_sum / neighbors_count
            alignment_force = self.alignment_factor * (average_speed - self.velocity)
        if separation_count > 0:
            separation_force = separation_sum / separation_count
        if self.predator is not None:
            predator_distance = self.position.distance_to(self.predator.position)
            if predator_distance < self.neighborhood_radius:
                direction_from_predator = self.position - self.predator.position
                # tworzymy wektor odwrotny od predatora
                if direction_from_predator.length() > 0:
                    fear_force = direction_from_predator.normalize() * (
                        self.neighborhood_radius - predator_distance
                    )
        food_force = self.get_food_influence()
        return (
            alignment_force
            + cohesion_force
            + separation_force
            + fear_force
            + food_force
        )

    def set_boids(self, boids: List["Boid"]) -> None:
        self.boids = boids

    def set_predator(self, predator: "Predator") -> None:
        self.predator = predator

    def set_food_group(self, food_group: pg.sprite.Group) -> None:
        self.food_group = food_group
