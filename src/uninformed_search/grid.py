"""Weighted grid maps used by the navigation search problem."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import ClassVar, Collection, Iterable, Sequence

Coordinate = tuple[int, int]


@dataclass(frozen=True, slots=True)
class GridMap:
    """A four-direction grid where entering a cell has a positive cost."""

    rows: int
    columns: int
    start: Coordinate
    goal: Coordinate
    blocked: frozenset[Coordinate]
    weights: tuple[tuple[int, ...], ...]

    _DIRECTIONS: ClassVar[tuple[Coordinate, ...]] = (
        (-1, 0),
        (0, 1),
        (1, 0),
        (0, -1),
    )

    def __post_init__(self) -> None:
        if type(self.rows) is not int or type(self.columns) is not int:
            raise TypeError("rows and columns must be integers")
        if self.rows < 1 or self.columns < 1:
            raise ValueError("rows and columns must be at least 1")

        normalized_weights = tuple(tuple(row) for row in self.weights)
        normalized_blocked = frozenset(self.blocked)
        object.__setattr__(self, "weights", normalized_weights)
        object.__setattr__(self, "blocked", normalized_blocked)

        if len(normalized_weights) != self.rows or any(
            len(row) != self.columns for row in normalized_weights
        ):
            raise ValueError("weights must contain one value for every grid cell")
        if any(
            type(weight) is not int or weight < 1
            for row in normalized_weights
            for weight in row
        ):
            raise ValueError("cell weights must be positive integers")

        self._require_coordinate(self.start, "start")
        self._require_coordinate(self.goal, "goal")
        for cell in normalized_blocked:
            self._require_coordinate(cell, "blocked cell")
        if self.start in normalized_blocked or self.goal in normalized_blocked:
            raise ValueError("start and goal cells cannot be blocked")

    @classmethod
    def uniform(
        cls,
        rows: int,
        columns: int,
        *,
        start: Coordinate = (0, 0),
        goal: Coordinate | None = None,
        blocked: Collection[Coordinate] = (),
        weight: int = 1,
    ) -> GridMap:
        """Build a grid whose traversable cells all have the same cost."""

        if type(rows) is not int or type(columns) is not int:
            raise TypeError("rows and columns must be integers")
        if rows < 1 or columns < 1:
            raise ValueError("rows and columns must be at least 1")
        if type(weight) is not int or weight < 1:
            raise ValueError("weight must be a positive integer")
        destination = (rows - 1, columns - 1) if goal is None else goal
        weights = tuple(tuple(weight for _ in range(columns)) for _ in range(rows))
        return cls(rows, columns, start, destination, frozenset(blocked), weights)

    @property
    def traversable_count(self) -> int:
        """Return the number of cells available to search."""

        return self.rows * self.columns - len(self.blocked)

    def contains(self, cell: Coordinate) -> bool:
        """Return whether a coordinate is inside the grid."""

        return (
            isinstance(cell, tuple)
            and len(cell) == 2
            and all(type(value) is int for value in cell)
            and 0 <= cell[0] < self.rows
            and 0 <= cell[1] < self.columns
        )

    def is_open(self, cell: Coordinate) -> bool:
        """Return whether a cell can be visited."""

        return self.contains(cell) and cell not in self.blocked

    def neighbors(self, state: Coordinate) -> tuple[Coordinate, ...]:
        """Return open neighbors in up, right, down, left order."""

        if not self.is_open(state):
            raise ValueError(f"state {state!r} is not an open grid cell")
        row, column = state
        candidates = (
            (row + row_change, column + column_change)
            for row_change, column_change in self._DIRECTIONS
        )
        return tuple(cell for cell in candidates if self.is_open(cell))

    def step_cost(self, current: Coordinate, neighbor: Coordinate) -> float:
        """Return the cost of entering an adjacent open cell."""

        if not self.is_open(current) or not self.is_open(neighbor):
            raise ValueError("both cells in a move must be open")
        distance = abs(current[0] - neighbor[0]) + abs(current[1] - neighbor[1])
        if distance != 1:
            raise ValueError("a move must connect adjacent cells")
        return float(self.weights[neighbor[0]][neighbor[1]])

    def is_valid_path(self, path: Sequence[Coordinate]) -> bool:
        """Check that a path connects this grid's start and goal."""

        if not path or path[0] != self.start or path[-1] != self.goal:
            return False
        return all(
            neighbor in self.neighbors(current)
            for current, neighbor in zip(path, path[1:])
        )

    def render(self, path: Iterable[Coordinate] = ()) -> str:
        """Render the grid using S, G, #, and * for special cells."""

        path_cells = set(path)
        path_cells.discard(self.start)
        path_cells.discard(self.goal)
        cell_width = max(
            1,
            max(len(str(weight)) for row in self.weights for weight in row),
        )
        rendered_rows: list[str] = []
        for row in range(self.rows):
            rendered_cells: list[str] = []
            for column in range(self.columns):
                cell = (row, column)
                if cell == self.start:
                    value = "S"
                elif cell == self.goal:
                    value = "G"
                elif cell in self.blocked:
                    value = "#"
                elif cell in path_cells:
                    value = "*"
                else:
                    value = str(self.weights[row][column])
                rendered_cells.append(value.rjust(cell_width))
            rendered_rows.append(" ".join(rendered_cells))
        return "\n".join(rendered_rows)

    def _require_coordinate(self, cell: Coordinate, label: str) -> None:
        if not self.contains(cell):
            raise ValueError(f"{label} {cell!r} is outside the grid")


def generate_random_grid(
    rows: int,
    columns: int,
    *,
    obstacle_rate: float = 0.2,
    min_weight: int = 1,
    max_weight: int = 9,
    seed: int | None = None,
    start: Coordinate = (0, 0),
    goal: Coordinate | None = None,
    ensure_solvable: bool = True,
) -> GridMap:
    """Generate a reproducible random weighted grid.

    When ``ensure_solvable`` is true, a random monotonic route between the
    endpoints is protected from obstacles before the other cells are sampled.
    """

    if type(rows) is not int or type(columns) is not int:
        raise TypeError("rows and columns must be integers")
    if rows < 1 or columns < 1:
        raise ValueError("rows and columns must be at least 1")
    if not isinstance(obstacle_rate, (int, float)) or isinstance(
        obstacle_rate, bool
    ):
        raise TypeError("obstacle rate must be a number")
    if not 0.0 <= float(obstacle_rate) <= 1.0:
        raise ValueError("obstacle rate must be between 0 and 1")
    if type(min_weight) is not int or type(max_weight) is not int:
        raise TypeError("weight bounds must be integers")
    if min_weight < 1 or max_weight < min_weight:
        raise ValueError("weight bounds must be positive and ordered")
    if seed is not None and type(seed) is not int:
        raise TypeError("seed must be an integer or None")
    if type(ensure_solvable) is not bool:
        raise TypeError("ensure_solvable must be a boolean")

    destination = (rows - 1, columns - 1) if goal is None else goal
    _validate_endpoint(start, rows, columns, "start")
    _validate_endpoint(destination, rows, columns, "goal")

    generator = random.Random(seed)
    protected = (
        _random_route(start, destination, generator)
        if ensure_solvable
        else {start, destination}
    )
    blocked = frozenset(
        (row, column)
        for row in range(rows)
        for column in range(columns)
        if (row, column) not in protected and generator.random() < obstacle_rate
    )
    weights = tuple(
        tuple(generator.randint(min_weight, max_weight) for _ in range(columns))
        for _ in range(rows)
    )
    return GridMap(rows, columns, start, destination, blocked, weights)


def _random_route(
    start: Coordinate,
    goal: Coordinate,
    generator: random.Random,
) -> set[Coordinate]:
    route = {start}
    current = start
    while current != goal:
        row, column = current
        choices: list[Coordinate] = []
        if row != goal[0]:
            row_step = 1 if goal[0] > row else -1
            choices.append((row + row_step, column))
        if column != goal[1]:
            column_step = 1 if goal[1] > column else -1
            choices.append((row, column + column_step))
        current = generator.choice(choices)
        route.add(current)
    return route


def _validate_endpoint(
    cell: Coordinate,
    rows: int,
    columns: int,
    label: str,
) -> None:
    if (
        not isinstance(cell, tuple)
        or len(cell) != 2
        or any(type(value) is not int for value in cell)
        or not (0 <= cell[0] < rows and 0 <= cell[1] < columns)
    ):
        raise ValueError(f"{label} {cell!r} is outside the grid")
