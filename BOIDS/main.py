import os

# TODO: Drapieżniki, pożywienie, odpoczynek
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg
from predator import Predator
from slider import Slider

from boids import Boid

BOIDS_NUM = 100


class Simulation:
    def __init__(self) -> None:
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 500, 500
        self.timer_event = pg.USEREVENT + 1

    def on_init(self) -> None:

        pg.init()

        self._display_surf = pg.display.set_mode(
            size=self.size,
            flags=pg.SCALED,
            vsync=1,
        )
        self.background = pg.Surface(self._display_surf.get_size()).convert_alpha()
        self.background.fill((0, 0, 0))
        pg.display.set_caption(title="boids")

        self.clock = pg.time.Clock()
        # ustawiamy timer na 30s
        pg.time.set_timer(self.timer_event, 30000)
        self._running = True

        self.all_sprites_group = pg.sprite.Group()

        self.boids = pg.sprite.Group()
        for _ in range(BOIDS_NUM):
            boid = Boid()
            self.boids.add(boid)
            self.all_sprites_group.add(boid)
        for boid in self.boids:
            boid.set_boids(boids=self.boids)

        self.predators = pg.sprite.Group()
        predator = Predator()
        predator.set_prey(boids=self.boids)
        self.all_sprites_group.add(predator)
        self.predators.add(predator)

        self.cohesion_slider = Slider(
            position=(self.width - 100, 50),
            size=(100, 1),
            initial_value=0.5,
            minimum_value=0,
            maximum_value=100,
            button_width=8,
            button_height=8,
            slider_name="Cohesion",
        )

        self.separation_slider = Slider(
            position=(self.width - 100, 125),
            size=(100, 1),
            initial_value=0.5,
            minimum_value=0,
            maximum_value=100,
            button_width=8,
            button_height=8,
            slider_name="Separation",
        )

        self.alignment_slider = Slider(
            position=(self.width - 100, 200),
            size=(100, 1),
            initial_value=0.5,
            minimum_value=0,
            maximum_value=100,
            button_width=8,
            button_height=8,
            slider_name="Alignment",
        )

        self.sliders = pg.sprite.Group()

        self.sliders.add(self.cohesion_slider)
        self.sliders.add(self.separation_slider)
        self.sliders.add(self.alignment_slider)

        self.all_sprites_group.add(self.cohesion_slider)
        self.all_sprites_group.add(self.separation_slider)
        self.all_sprites_group.add(self.alignment_slider)

    def on_event(self, event) -> None:
        if event.type == pg.QUIT:
            self._running = False
        for slider in self.sliders.sprites():
            slider.handle_event(event)
        if event.type == self.timer_event:
            # co 30 sekund wyłącz tryb ataku predatorowi
            pred = self.predators.sprites()[0]
            pred.attack = not pred.attack

    def on_loop(self) -> None:
        for boid in self.boids:
            boid.cohesion_factor = self.cohesion_slider.get_value() * 0.001
            boid.separation_factor = self.separation_slider.get_value() * 0.01
            boid.alignment_factor = self.alignment_slider.get_value() * 0.01

        self.all_sprites_group.update()

    def on_render(self) -> None:
        self.all_sprites_group.clear(surface=self._display_surf, bgd=self.background)
        self.all_sprites_group.draw(surface=self._display_surf)
        pg.display.update()
        self.clock.tick(60)

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

    # profile.run("main()", sort="ncalls")
