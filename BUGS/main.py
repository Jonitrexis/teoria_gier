import numpy as np
import pygame as pg
from consts import TILE_SIZE
from food import Food
from spatial_grid import SpatialGrid

from bugs import Bug


class Simulation:
    def __init__(self) -> None:
        self._running = True
        self._display_surf = None
        self._paused = False
        self.size = self.width, self.height = 1001, 1001
        self.food_event = pg.USEREVENT + 1
        self.spatial_grid = SpatialGrid(
            self.size[0],
            self.size[1],
            TILE_SIZE * 3,
        )
        self.food_group = pg.sprite.Group()
        self.bugs_group = pg.sprite.Group()
        self.clock = None
        self.background = None

    def populate(self):
        """Tworzy początkową populację jedzenia i bugów."""
        for _ in range(round(self.width * 10)):
            food = Food(spatial_grid=self.spatial_grid)
            self.food_group.add(food)
        for _ in range(60):
            Bug(
                position=pg.math.Vector2(
                    (
                        np.random.random() * self.width,
                        np.random.random() * self.height,
                    )
                ),
                food_group=self.food_group,
                spatial_grid=self.spatial_grid,
                bugs_group=self.bugs_group,
            )

    def on_init(self) -> None:
        """Inicjalizuje Pygame i zasoby symulacji."""

        pg.init()

        pg.time.set_timer(self.food_event, 2)

        self._display_surf = pg.display.set_mode(
            size=self.size,
            vsync=1,
        )
        self.background = pg.Surface(self._display_surf.get_size()).convert()
        self.background.fill((0, 0, 0))
        pg.display.set_caption("BUGS LIFE (1998)")

        self.clock = pg.time.Clock()
        self._running = True
        self.populate()
        return True

    def spawn_food(self) -> None:
        """Tworzy i dodaje nowe jedzenie."""
        new_food = Food(spatial_grid=self.spatial_grid)
        self.food_group.add(new_food)

    def on_event(self, event) -> None:
        """Obsługuje zdarzenia Pygame."""
        if event.type == pg.QUIT:
            self._running = False
        if event.type == pg.KEYDOWN and self._paused:
            if event.key == pg.K_r:
                self.__init__()
                self.on_init()
        if event.type == self.food_event and not self._paused:
            self.spawn_food()

    def on_loop(self) -> None:
        """Aktualizuje logikę symulacji."""
        self.bugs_group.update()
        if not self.bugs_group.sprites() and not self._paused:
            self._paused = True

    def on_render(self) -> None:
        """Rysuje elementy symulacji na ekranie."""
        self._display_surf.fill((0, 0, 0))
        self.food_group.draw(surface=self._display_surf)
        self.bugs_group.draw(surface=self._display_surf)
        if self._paused:
            font = pg.font.SysFont(None, 36)
            text = font.render(
                "Wszystkie bugi nie żyją,"
                + "\n\n by zrestartować symulację"
                + "\n\n naciśnij R",
                True,
                (255, 255, 255),
            )
            text_rect = text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2,
                )
            )
            self._display_surf.blit(text, text_rect)
        pg.display.update()
        self.clock.tick(3000)

    def on_cleanup(self) -> None:
        pg.quit()

    # our main game loop

    def on_execute(self) -> None:
        if self.on_init() is False:
            self._running = False
        while self._running:
            for event in pg.event.get():
                self.on_event(event=event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


def main() -> None:
    sim = Simulation()
    sim.on_execute()


if __name__ == "__main__":
    main()
    # import cProfile as profile

    # profile.run("main()", sort="tottime")
