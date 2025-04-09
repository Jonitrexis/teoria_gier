from typing import List

import numpy as np
import pygame as pg
from vehicle import Vehicle

from boids import Boid


class Predator(Vehicle):
    max_acceleration = 0.05

    max_speed = 1.0
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
    d_min = 40
    # waga losowych zakłóceń
    disturbance = 0.01

    closest_boid: Boid = None

    attack = False

    def __init__(self) -> None:
        super().__init__(color=(0, 239, 255), max_speed=self.max_speed)

    def update(self) -> None:
        super().update(self.pursue(), self.max_acceleration)

    def pursue(self) -> pg.Vector2:
        # TODO dodać logikę podążania za boidami:
        # TODO jeśli widzi boida, to idzie w atak
        # Zmieniamy prędkość, by poszedł w kierunku boida
        # zasada separacji odwrócona
        # przez ileś iteracji w trybie ataku
        # w trybie ataku Vmax i w trybie spoczynku V_max mniejsze
        # można z trybu spójności, predator leci w stronę stada

        if self.attack:
            self.max_speed = 2.1
            self.max_acceleration = 0.3
            print("PREDATOR W TRYBIE ATAKU")
        else:
            self.max_speed = 1.0
            self.max_acceleration = 0.05
        return self.find_nearest_boid()

    def find_nearest_boid(self):
        separation_force = pg.Vector2(0, 0)
        cached_angle_rad = np.radians(self.cached_angle)
        perception_half = np.radians(self.perception / 2)
        distance_min = np.inf
        for boid in self.boids:
            distance_to_boid = self.position.distance_to(boid.position)
            if distance_to_boid < distance_min:
                distance_min = distance_to_boid
                self.closest_boid = boid
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
            if angle_diff < perception_half:
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

    def set_prey(self, boids: List["Boid"]):
        self.boids = boids
