from typing import Tuple

import numpy as np
import pygame as pg
from pygame import Vector2, gfxdraw


class Vehicle(pg.sprite.Sprite):

    def __init__(self, color: Tuple[int, int, int], max_speed: float) -> None:

        super().__init__()
        # pg.SRCALPHA mówi, że ma przezroczystość obrazek
        self.image: pg.Surface = pg.Surface((15, 15), pg.SRCALPHA)
        # trójkącik o zadanym kolorze
        self.TRIANGLE_POINTS = [(15, 5), (0, 2), (0, 8)]
        gfxdraw.filled_polygon(
            self.image,
            self.TRIANGLE_POINTS,
            pg.Color(*color, 255),
        )
        # promień naszego pojazdu, by zderzenia były lepsze
        self.radius: int = self.image.get_width() // 2
        # losowy kąt początkowy
        self.direction: float = np.random.uniform(
            low=np.radians(0),
            high=np.radians(360),
        )
        # losowa początkowa pozycja
        self.position: Vector2 = pg.Vector2(
            x=np.random.uniform(0, pg.display.get_surface().get_width()),
            y=np.random.uniform(0, pg.display.get_surface().get_height()),
        )
        # cosinus reprezezntuje x składową wektora, tj.znając kąt wiemy ile
        # się przesunąć wzdłóż iksowej, sinus analogicznie
        self.velocity: Vector2 = pg.Vector2(
            x=np.cos(self.direction),
            y=np.sin(self.direction),
        )

        self.rect: pg.Rect = self.image.get_rect(center=self.position)

        # cache, bo gra nie wyrabia przerysowując tyle razy trójkąciki
        self.last_rotation_angle: int = 0
        self.original_image: pg.Surface = self.image.copy()
        self.angle_cache: dict = {}

        self.acceleration: pg.Vector2 = Vector2(0, 0)
        self.max_speed: float = max_speed
        # waga losowych zakłóceń
        self.disturbance_weight: float = 0.01

    def update(
        self,
        external_forces: pg.Vector2,
        max_acceleration: float,
    ) -> None:
        self.move(
            external_forces=external_forces,
            max_acceleration=max_acceleration,
        )

    def move(
        self,
        external_forces: pg.Vector2,
        max_acceleration: float,
    ) -> None:
        # ograniczenie maksymalnego przyspieszenia
        self.acceleration = self.clamp_force(
            external_forces,
            max_acceleration,
        )
        self.velocity += self.acceleration
        # zaburzenia
        self.velocity += self.add_noise()

        # ograniczenie maksymalnej prędkości
        self.velocity = self.clamp_force(
            self.velocity,
            self.max_speed,
        )
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
            angle = round(
                np.degrees(
                    np.arctan2(
                        self.velocity.y,
                        self.velocity.x,
                    )
                )
            )
            # jeśli kąt się zmienił o mniej niż 1 stopień, to nie kręcimy
            if abs(angle - self.last_rotation_angle) > 1:
                # bez sensu kręcić tyle razy trójkącikiem, mamy cashe
                if angle not in self.angle_cache:
                    self.angle_cache[angle] = pg.transform.rotate(
                        self.original_image, -angle
                    )

                self.image = self.angle_cache[angle]
            self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen: pg.SurfaceType) -> None:
        screen.blit(source=self.image, dest=self.rect)

    def clamp_force(self, force: pg.Vector2, max_force: float) -> pg.Vector2:
        if force.length() > max_force:
            return force.normalize() * max_force
        else:
            return force

    def add_noise(self) -> pg.Vector2:
        return self.disturbance_weight * pg.Vector2(
            np.sin(np.random.uniform(low=np.radians(0), high=np.radians(360))),
            np.cos(np.random.uniform(low=np.radians(0), high=np.radians(360))),
        )
