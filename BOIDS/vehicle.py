import random
from typing import Tuple

import numpy as np
import pygame as pg
from pygame import Vector2, gfxdraw


class Vehicle(pg.sprite.Sprite):

    # pygame.SRCALPHA mówi, że nowa powierzchnia potrzebuje
    # posiadać kanał alfa

    def __init__(self, color: Tuple[int, int, int], max_speed: float) -> None:

        super().__init__()
        # pg.SRCALPHA mówi, że ma przezroczystość obrazek
        self.image = pg.Surface((15, 15), pg.SRCALPHA)
        # trójkącik o zadanym kolorze
        gfxdraw.filled_polygon(
            self.image,
            [(15, 5), (0, 2), (0, 8)],
            pg.Color(*color, 255),
        )
        # losowy kąt początkowy
        self.direction: float = np.random.uniform(
            low=np.radians(0),
            high=np.radians(360),
        )
        # losowa początkowa pozycja
        self.position: Vector2 = pg.Vector2(
            x=random.uniform(0, pg.display.get_surface().get_width()),
            y=random.uniform(0, pg.display.get_surface().get_height()),
        )
        # cosinus reprezezntuje x składową wektora, tj.znając kąt wiemy ile
        # się przesunąć wzdłóż iksowej, sinus analogicznie
        self.velocity: Vector2 = pg.Vector2(
            x=np.cos(self.direction),
            y=np.sin(self.direction),
        )

        self.rect: pg.Rect = self.image.get_rect(center=self.position)

        # cache, bo gra nie wyrabia przerysowując tyle razy trójkąciki
        self.cached_angle: int = 0
        self.original_image = self.image.copy()
        self.angle_cache = {}

        self.acceleration = Vector2(0, 0)
        self.max_speed = max_speed
        # waga losowych zakłóceń
        self.disturbance = 0.01

    def update(self, external_forces: pg.Vector2, max_acceleration: float):
        self.move(
            external_forces=external_forces,
            max_acceleration=max_acceleration,
        )

    def move(self, external_forces: pg.Vector2, max_acceleration: float) -> None:
        # siły działające
        self.acceleration = external_forces
        # ograniczenie maksymalnego przyspieszenia
        if self.acceleration.length() > max_acceleration:
            self.acceleration = self.acceleration.normalize() * max_acceleration
        self.velocity += self.acceleration
        # zaburzenia
        self.velocity += self.disturbance * pg.Vector2(
            np.sin(np.random.uniform(low=np.radians(0), high=np.radians(360))),
            np.cos(np.random.uniform(low=np.radians(0), high=np.radians(360))),
        )

        # ograniczenie maksymalnej prędkości
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * (self.max_speed)
        self.position += self.velocity
        self.avoid_edge()

        self.rect.center = self.position
        self.update_rotation()

    def avoid_edge(self) -> None:
        screen_width, screen_height = pg.display.get_surface().get_size()

        # odbijanie jednostek od brzegów ekranu
        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x = -self.velocity.x

        elif self.position.x > screen_width:
            self.position.x = screen_width
            self.velocity.x = -self.velocity.x

        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y = -self.velocity.y

        elif self.position.y > screen_height:
            self.position.y = screen_height
            self.velocity.y = -self.velocity.y

    def update_rotation(self) -> None:
        # tylko jeśli jest prędkość większa od 0, bo inaczej się kręcimy
        if self.velocity.length() > 0.1:
            # liczymy kąt z prędkości boida
            angle = round(np.degrees(np.arctan2(self.velocity.y, self.velocity.x)))
            # jeśli kąt się zmienił o mniej niż 1 stopień, to nie kręcimy
            if abs(angle - self.cached_angle) > 1:
                # bez sensu kręcić tyle razy trójkącikiem, mamy cashe
                if angle not in self.angle_cache:
                    self.angle_cache[angle] = pg.transform.rotate(
                        self.original_image, -angle
                    )

                self.image = self.angle_cache[angle]
            self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen: pg.SurfaceType) -> None:
        screen.blit(source=self.image, dest=self.rect)
