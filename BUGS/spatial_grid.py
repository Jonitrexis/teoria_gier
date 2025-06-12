from collections import defaultdict

import pygame as pg


class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(set)
        self.width = width
        self.height = height

    def _get_cell(self, pos: pg.math.Vector2) -> tuple[int, int] | None:
        """Pobiera współrzędne komórki na podstawie pozycji."""
        x, y = int(pos.x // self.cell_size), int(pos.y // self.cell_size)
        if 0 <= x < self.width and 0 <= y < self.height:
            return (x, y)
        return None

    def add(self, sprite) -> None:
        """Dodaje sprite do odpowiedniej komórki."""
        cell = self._get_cell(sprite.position)
        if cell:
            self.grid[cell].add(sprite)
            sprite._spatial_cell = cell

    def remove(self, sprite) -> None:
        """Usuwa sprite z jego aktualnej komórki."""
        cell = getattr(sprite, "_spatial_cell", None)
        if cell and sprite in self.grid[cell]:
            self.grid[cell].remove(sprite)
        sprite._spatial_cell = None

    def update(self, sprite) -> None:
        """Aktualizuje położenie sprite'a w siatce, jeśli zmienił komórkę."""
        new_cell = self._get_cell(sprite.position)
        old_cell = getattr(sprite, "_spatial_cell", None)
        if new_cell != old_cell:
            if old_cell:
                self.grid[old_cell].discard(sprite)
            if new_cell:
                self.grid[new_cell].add(sprite)
            sprite._spatial_cell = new_cell

    def get_nearby(self, sprite) -> list:
        """Zwraca listę sprite'ów z sąsiednich komórek (włączając aktualną)."""
        cell = self._get_cell(sprite.position)
        if not cell:
            return
        sx, sy = cell
        seen = set()  # by nie powtórzyć sprite’ów
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                c = (sx + dx, sy + dy)
                if c in self.grid:
                    for s in self.grid[c]:
                        if s is not sprite and s not in seen:
                            seen.add(s)
                            yield s
