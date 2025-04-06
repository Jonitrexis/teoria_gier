import numpy as np
import pygame as pg

from vehicle import Vehicle


class Predator(Vehicle):
    max_acceleration = 0.05

    max_speed = 1.0
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
    # waga losowych zakłóceń
    disturbance = 0.01

    def __init__(self) -> None:
        super().__init__(color=(0, 239, 255), max_speed=self.max_speed)

    def update(self) -> None:
        super().update(self.pursue(), self.max_acceleration)

    def pursue(self) -> pg.Vector2:
        # TODO:
        return pg.Vector2(
            np.random.uniform(
                low=-5,
                high=5,
            ),
            np.random.uniform(
                low=-5,
                high=5,
            ),
        )
