import pygame as pg


class Food(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        radius = 3
        diameter = radius * 2

        self.image = pg.Surface((diameter, diameter), pg.SRCALPHA)
        pg.gfxdraw.filled_circle(
            self.image,
            radius,
            radius,
            radius,
            (0, 255, 0),
        )
        pg.gfxdraw.aacircle(
            self.image,
            radius,
            radius,
            radius,
            (0, 255, 0),
        )

        self.rect = self.image.get_rect(center=position)
