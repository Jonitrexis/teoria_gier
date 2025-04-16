from typing import List, Tuple

import numpy as np

# pygame-ce zamiast pygame
import pygame as pg
from vehicle import Vehicle

from boids import Boid


class Predator(Vehicle):
    MAX_ATTACK_SPEED = 2.1
    MAX_ATTACK_ACCELERATION = 0.3
    MAX_NORMAL_SPEED = 1.0
    MAX_NORMAL_ACCELERATION = 0.05
    D_MIN_ATTACK = 100
    D_MIN_NORMAL = 40

    max_acceleration = MAX_NORMAL_ACCELERATION

    max_speed = MAX_NORMAL_SPEED
    # kąt obserwacji
    perception = 120
    # promień sąsiedzctwa
    neighborhood_radius = 300
    # waga wyrównania
    alignment_factor = 1
    # waga spójności
    cohesion_factor = 0.1
    # waga rozdzielności
    separation_factor = -10
    # odległośc minimalna
    d_min = D_MIN_NORMAL
    # waga losowych zakłóceń
    disturbance = 0.01

    closest_boid: Boid = None

    attack = False

    base_color: Tuple[int, int, int] = (0, 239, 255)
    attack_color: Tuple[int, int, int] = (255, 0, 0)

    def __init__(self) -> None:
        super().__init__(color=self.base_color, max_speed=self.max_speed)
        # inicjalizacja listy boidów
        self.boids = []

    def update(self) -> None:
        self.update_color()
        super().update(self.pursue(), self.max_acceleration)

    def update_color(self) -> None:
        # TODO: znaleźć błąd dlaczego miga kilka razy,
        # a później zmienia kolor na bazowy
        self.original_image.fill((0, 0, 0, 0))
        if self.attack:
            pg.gfxdraw.filled_polygon(
                self.original_image,
                self.TRIANGLE_POINTS,
                self.attack_color,
            )
        else:
            pg.gfxdraw.filled_polygon(
                self.original_image,
                self.TRIANGLE_POINTS,
                self.base_color,
            )

    def pursue(self) -> pg.Vector2:
        if self.attack:
            self.max_speed = self.MAX_ATTACK_SPEED
            self.max_acceleration = self.MAX_ATTACK_ACCELERATION
            self.d_min = self.D_MIN_ATTACK

        else:
            self.d_min = self.D_MIN_NORMAL
            self.max_speed = self.MAX_NORMAL_SPEED
            self.max_acceleration = self.MAX_NORMAL_ACCELERATION
        return self.find_nearest_boid()

    def find_nearest_boid(self) -> pg.Vector2:
        separation_force = pg.Vector2(0, 0)
        cached_angle_rad = np.radians(self.last_rotation_angle)
        perception_half = np.radians(self.perception / 2)
        distance_min = np.inf
        if not self.boids:
            # brak boidów, brak akcji
            return pg.Vector2(0, 0)
        for boid in self.boids:
            distance_to_boid = self.position.distance_to(boid.position)
            if distance_to_boid < distance_min:
                distance_min = distance_to_boid
                self.closest_boid = boid
        if self.closest_boid is None:
            # brak najbliższego boida, nie robimy nic
            return pg.Vector2(0, 0)
        if distance_min < self.neighborhood_radius:
            angle_to_boid = np.arctan2(
                self.closest_boid.position.y - self.position.y,
                self.closest_boid.position.x - self.position.x,
            )
            # obliczamy różnicę między kątami (w radianach)
            angle_diff = np.abs(cached_angle_rad - angle_to_boid)

            # sprawdzamy różnicę kątów, jeśli jest większa niż 180,
            #  to zmniejszamy ją
            if angle_diff > np.pi:
                angle_diff = 2 * np.pi - angle_diff
            # sprawdzamy, czy boid jest w zasięgu percepcji
            if angle_diff < perception_half:
                # jeśli odległość jest mniejsza niż minimalna,
                # obliczamy siłę separacji i używamy jej z przeciwnym
                # znakiem by nasz predator podążał za boidami
                if 0 < abs(distance_min) < self.d_min:
                    separation_strength = self.separation_factor * (
                        (1 - (self.d_min / abs(distance_min)))
                        * (self.closest_boid.position - self.position)
                    )
                    separation_force += separation_strength
        # jeśli jesteśmy w trybie ataku to lecimy za najbliższym
        # w innym przypadku latamy losowo
        return (
            separation_force
            if self.attack
            else pg.Vector2(
                np.random.uniform(
                    low=-5,
                    high=5,
                ),
                np.random.uniform(
                    low=-5,
                    high=5,
                ),
            )
        )

    def set_prey(self, boids: List[Boid]) -> None:
        self.boids = boids
