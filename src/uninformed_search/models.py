"""Shared interfaces and result types used by every search algorithm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Hashable, Iterable, Mapping, Protocol, TypeVar

State = TypeVar("State", bound=Hashable)


class SearchProblem(Protocol[State]):
    """The minimum interface needed by the search algorithms."""

    start: State
    goal: State

    def neighbors(self, state: State) -> Iterable[State]:
        """Return states that can be reached from ``state`` in one move."""

    def step_cost(self, current: State, neighbor: State) -> float:
        """Return the nonnegative cost of moving to ``neighbor``."""


@dataclass(frozen=True, slots=True)
class SearchMetrics:
    """Measurements collected during one complete search.

    ``generated_nodes`` includes the start state and every state accepted into
    a frontier. ``expanded_nodes`` counts states whose neighbors are examined.
    """

    expanded_nodes: int
    generated_nodes: int
    max_frontier_size: int
    elapsed_seconds: float
    iterations: int = 1

    def __post_init__(self) -> None:
        integer_fields = (
            self.expanded_nodes,
            self.generated_nodes,
            self.max_frontier_size,
        )
        if any(value < 0 for value in integer_fields):
            raise ValueError("node and frontier measurements cannot be negative")
        if self.elapsed_seconds < 0:
            raise ValueError("elapsed time cannot be negative")
        if self.iterations < 1:
            raise ValueError("iterations must be at least 1")


@dataclass(frozen=True, slots=True)
class SearchResult(Generic[State]):
    """A path and its measurements, or a consistent failed-search result."""

    algorithm: str
    found: bool
    path: tuple[State, ...]
    cost: float | None
    metrics: SearchMetrics

    def __post_init__(self) -> None:
        if not self.algorithm.strip():
            raise ValueError("algorithm name cannot be empty")
        if self.found and (not self.path or self.cost is None):
            raise ValueError("a successful search needs a path and cost")
        if not self.found and (self.path or self.cost is not None):
            raise ValueError("a failed search cannot contain a path or cost")
        if self.cost is not None and self.cost < 0:
            raise ValueError("path cost cannot be negative")

    @property
    def depth(self) -> int | None:
        """Return the number of moves in the path, or ``None`` on failure."""

        return len(self.path) - 1 if self.found else None


def reconstruct_path(
    parents: Mapping[State, State | None], goal: State
) -> tuple[State, ...]:
    """Reconstruct a start-to-goal path from a parent mapping."""

    path: list[State] = []
    current: State | None = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return tuple(path)


def calculate_path_cost(
    problem: SearchProblem[State], path: tuple[State, ...]
) -> float:
    """Add the action costs along a path."""

    return sum(
        problem.step_cost(current, neighbor)
        for current, neighbor in zip(path, path[1:])
    )
