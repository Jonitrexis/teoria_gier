from collections import defaultdict

import pygame as pg


class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        self.width = width
        self.height = height

    def _get_cell(self, position: pg.math.Vector2) -> tuple[int, int]:
        """Pobiera współrzędne komórki na podstawie pozycji."""
        x = int(position.x // self.cell_size)
        y = int(position.y // self.cell_size)
        return x, y

    def add(self, sprite) -> None:
        """Dodaje sprite do odpowiedniej komórki."""
        cell = self._get_cell(sprite.position)
        self.grid[cell].append(sprite)

    def remove(self, sprite) -> None:
        """Usuwa sprite z jego aktualnej komórki."""
        cell = self._get_cell(sprite.position)
        if sprite in self.grid[cell]:
            self.grid[cell].remove(sprite)

    def update(self, sprite) -> None:
        """Aktualizuje położenie sprite'a w siatce, jeśli zmienił komórkę."""
        old_cell = self._get_cell(sprite.position - sprite.move_vector)
        new_cell = self._get_cell(sprite.position)
        if old_cell != new_cell:
            if (
                sprite in self.grid[old_cell]
            ):  # Dodano sprawdzenie, czy sprite jest w starej komórce
                self.grid[old_cell].remove(sprite)
            self.grid[new_cell].append(sprite)

    def get_nearby(self, sprite) -> list:
        """Zwraca listę sprite'ów z sąsiednich komórek (włączając aktualną)."""
        cell = self._get_cell(sprite.position)
        nearby_sprites = set()  # Używamy set, aby uniknąć duplikatów
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nearby_cell = (cell[0] + dx, cell[1] + dy)
                if nearby_cell in self.grid:
                    nearby_sprites.update(self.grid[nearby_cell])
        return list(nearby_sprites)
