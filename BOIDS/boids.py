from typing import List

import numpy as np
import pygame as pg

from vehicle import Vehicle


class Boid(Vehicle):

    max_acceleration = 0.1

    max_speed = 2.0
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

    def __init__(self) -> None:
        super().__init__(color=(209, 125, 146), max_speed=self.max_speed)

    def update(self) -> None:
        # TODO: tryb ucieczki
        # czas przez ileś iteracji czas ucieczki
        # na przykład większa waga odnośnie predatora z zasady rozdzielności
        # bawić się regułam wpływania na boida, jeśli jest w trybie uciekania
        super().update(self.get_neighbors_influence(), self.max_acceleration)

    def get_neighbors_influence(self) -> pg.Vector2:
        cohesion_force = pg.Vector2(0, 0)
        average_position = pg.Vector2(0, 0)
        total_cohesion_alignment = 0
        total_separation = 0
        alignment_force = pg.Vector2(0, 0)
        average_speed = pg.Vector2(0, 0)
        separation_force = pg.Vector2(0, 0)

        sum_of_boids_position = pg.Vector2(0, 0)
        sum_of_boids_speed = pg.Vector2(0, 0)
        # zmieniamy na radiany,
        # bo to przyspiesza pracę (zamiast liczyć np.degrees co iterację)
        cached_angle_rad = np.radians(self.cached_angle)
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
                        sum_of_boids_position += boid.position
                        # alignment
                        sum_of_boids_speed += boid.velocity
                        total_cohesion_alignment += 1

                        direction = boid.position - self.position
                        # separation
                        if 0 < abs(distance) < self.d_min:
                            # zastosowanie wzoru na siłę separacji
                            separation_strength = self.separation_factor * (
                                (1 - (self.d_min / abs(distance))) * direction
                            )
                            separation_force += separation_strength
                            total_separation += 1
        if total_cohesion_alignment > 0:
            average_position = sum_of_boids_position / total_cohesion_alignment
            cohesion_force = self.cohesion_factor * (average_position - self.position)

            average_speed = sum_of_boids_speed / total_cohesion_alignment
            alignment_force = self.alignment_factor * (average_speed - self.velocity)
        if total_separation > 0:
            separation_force /= total_separation
        return alignment_force + cohesion_force + separation_force

    def set_boids(self, boids: List["Boid"]):
        self.boids = boids
