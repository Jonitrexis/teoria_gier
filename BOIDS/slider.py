from typing import Tuple

import pygame as pg


class Slider(pg.sprite.Sprite):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        initial_value: float,
        minimum_value: int,
        maximum_value: int,
        button_width: int,
        button_height: int,
        slider_name: str,
    ) -> None:
        super().__init__()
        self.position = position
        self.size = size
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        self.slider_name = slider_name

        # utwórz powierzchnię sprite’a'
        # powiększamy o miejsce na etykietę nad suwakiem.
        label_height = 20
        self.image = pg.Surface(
            (size[0], size[1] + label_height), pg.SRCALPHA
        ).convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.image.fill((0, 0, 0, 0))
        # pozycja slidera – rysowany jest na dole powierzchni sprite’a
        self.slider_rect = pg.Rect(0, label_height, size[0], size[1])
        # początkowa pozycja przycisku – określana jako procent szerokości
        init_px = size[0] * initial_value
        self.button_width = button_width
        self.button_height = button_height
        self.button_rect = pg.Rect(0, 0, button_width, button_height)
        self.button_rect.centerx = init_px
        self.button_rect.centery = self.slider_rect.centery

        self.button_grabbed = False

    def get_value(self) -> float:
        # wartość suwaka jako przeliczona z pozycji przycisku
        value_range = self.size[0]
        button_pos = self.button_rect.centerx
        return (button_pos / value_range) * (
            self.maximum_value - self.minimum_value
        ) + self.minimum_value

    def render_label(self) -> None:
        # rysuj etykietę na górze
        text = pg.font.Font(None, 15).render(
            f"{self.slider_name} {int(self.get_value())}", True, "white"
        )
        text_rect = text.get_rect(center=(self.image.get_width() // 2, 10))
        self.image.blit(text, text_rect)

    def update(self) -> None:
        # całkowicie wyczyść obraz (cały sprite)
        self.image.fill((0, 0, 0, 0))
        self.render_label()
        pg.draw.rect(self.image, "yellow", self.slider_rect)
        pg.draw.rect(self.image, "green", self.button_rect)

    def move_slider(self, new_x: int) -> None:
        # nowa lokalna pozycja przycisku (ograniczona do szerokości slidera)
        new_x = max(0, min(new_x, self.size[0]))
        self.button_rect.centerx = new_x

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # przeliczamy pozycję lokalną
                local = (
                    event.pos[0] - self.rect.left,
                    event.pos[1] - self.rect.top,
                )
                if self.button_rect.collidepoint(local):
                    self.button_grabbed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.button_grabbed = False
        elif event.type == pg.MOUSEMOTION:
            if self.button_grabbed:
                # przekształcamy globalny x na lokalny względem suwaka
                local_x = event.pos[0] - self.rect.left
                self.move_slider(local_x)
