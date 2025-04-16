import os

# ukrywamy prompt supportu pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import numpy as np
import pygame as pg
from food import Food
from predator import Predator
from slider import Slider

from boids import Boid

BOIDS_NUM = 100


class Simulation:
    def __init__(self) -> None:
        self._running = True
        self._display_surf = None
        self._paused = False
        self.size = self.width, self.height = 500, 500
        self.timer_event = pg.USEREVENT + 1
        self.food_event = pg.USEREVENT + 2

    def on_init(self) -> None:

        pg.init()

        self._display_surf = pg.display.set_mode(
            size=self.size,
            flags=pg.SCALED,
            vsync=1,
        )
        self.background = pg.Surface(self._display_surf.get_size())
        self.background.fill((0, 0, 0))
        pg.display.set_caption("boids")

        self.clock = pg.time.Clock()
        # ustawiamy timer zmiany trybu ataku na 30s
        pg.time.set_timer(self.timer_event, 30000)
        # pojawianie się jedzenia co 5 sekund
        pg.time.set_timer(self.food_event, 5000)
        self._running = True

        self.all_sprites_group = pg.sprite.Group()
        self.boids = pg.sprite.Group()
        self.predators = pg.sprite.Group()
        self.sliders = pg.sprite.Group()
        self.food_group = pg.sprite.Group()

        for _ in range(20):
            food = Food(
                position=(
                    np.random.randint(50, 450),
                    np.random.randint(50, 450),
                )
            )
            self.food_group.add(food)
            self.all_sprites_group.add(food)

        for _ in range(BOIDS_NUM):
            boid = Boid()
            self.boids.add(boid)
            self.all_sprites_group.add(boid)

        self.predator = Predator()
        self.predator.set_prey(boids=self.boids)
        self.all_sprites_group.add(self.predator)
        self.predators.add(self.predator)

        for boid in self.boids:
            boid.set_boids(boids=self.boids)
            boid.set_predator(predator=self.predator)
            boid.set_food_group(self.food_group)

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
        for slider in (
            self.cohesion_slider,
            self.separation_slider,
            self.alignment_slider,
        ):
            self.sliders.add(slider)
            self.all_sprites_group.add(slider)

    def spawn_food(self) -> None:
        x = np.random.randint(0, self._display_surf.get_width())
        y = np.random.randint(0, self._display_surf.get_height())
        new_food = Food((x, y))
        self.food_group.add(new_food)
        self.all_sprites_group.add(new_food)

    def on_event(self, event) -> None:
        if event.type == pg.QUIT:
            self._running = False
        # przekazywanie zdarzeń do suwaków
        for slider in self.sliders.sprites():
            slider.handle_event(event)
        # co 30 sekund wyłącz tryb ataku predatorowi
        if event.type == self.timer_event:
            self.predator.attack = not self.predator.attack
        if event.type == self.food_event and not self._paused:
            self.spawn_food()
        if event.type == pg.KEYDOWN and self._paused:
            if event.key == pg.K_r:
                self.__init__()
                self.on_init()

    def on_loop(self) -> None:
        # aktualizacja wartości boidów według wartości z suwaków
        for boid in self.boids:
            boid.cohesion_factor = self.cohesion_slider.get_value() * 0.001
            boid.separation_factor = self.separation_slider.get_value() * 0.01
            boid.alignment_factor = self.alignment_slider.get_value() * 0.01
        # sprawdzamy kolizję drapieżnika z boidami i jeśli jest w trybie ataku
        # to usuwamy zaatakowane boidy
        pg.sprite.spritecollide(
            sprite=self.predator,
            group=self.boids,
            dokill=self.predator.attack,
            collided=pg.sprite.collide_circle,
        )
        if len(self.boids) == 0 and not self._paused:
            print("Wszystkie boidy nie żyją. Pauza.")
            # zapauj symulację
            self._paused = True
        self.all_sprites_group.update()

    def on_render(self) -> None:
        self.all_sprites_group.clear(
            surface=self._display_surf,
            bgd=self.background,
        )
        self.all_sprites_group.draw(surface=self._display_surf)
        if self._paused:
            # zatrzymujemy predatora
            #
            self.predator.velocity = pg.Vector2(0, 0)
            font = pg.font.SysFont(None, 36)
            text = font.render(
                "Wszystkie boidy nie żyją,\n\n by zrestartować symulację\n\n naciśnij R",
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
