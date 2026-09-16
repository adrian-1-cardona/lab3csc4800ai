"""Iterative deepening depth-first search implementation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from time import perf_counter
from typing import Generic, Hashable, TypeVar

from uninformed_search.models import (
    SearchMetrics,
    SearchProblem,
    SearchResult,
    calculate_path_cost,
)

State = TypeVar("State", bound=Hashable)


@dataclass(frozen=True, slots=True)
class _DepthLimitedResult(Generic[State]):
    path: tuple[State, ...] | None
    cutoff: bool
    expanded_nodes: int
    generated_nodes: int
    max_frontier_size: int


def iterative_deepening_search(
    problem: SearchProblem[State],
    max_depth: int | None = None,
) -> SearchResult[State]:
    """Repeat depth-limited DFS until a shallowest path is found.

    A grid's automatic depth bound is one less than its traversable cell count,
    which is the longest useful simple path in a finite grid.
    """

    depth_bound = _resolve_depth_bound(problem, max_depth)
    started_at = perf_counter()
    total_expanded = 0
    total_generated = 0
    max_frontier_size = 0
    iterations = 0

    for depth_limit in range(depth_bound + 1):
        iterations += 1
        outcome = _depth_limited_search(problem, depth_limit)
        total_expanded += outcome.expanded_nodes
        total_generated += outcome.generated_nodes
        max_frontier_size = max(max_frontier_size, outcome.max_frontier_size)

        if outcome.path is not None:
            return SearchResult(
                algorithm="IDDFS",
                found=True,
                path=outcome.path,
                cost=calculate_path_cost(problem, outcome.path),
                metrics=SearchMetrics(
                    expanded_nodes=total_expanded,
                    generated_nodes=total_generated,
                    max_frontier_size=max_frontier_size,
                    elapsed_seconds=perf_counter() - started_at,
                    iterations=iterations,
                ),
            )
        if not outcome.cutoff:
            break

    return SearchResult(
        algorithm="IDDFS",
        found=False,
        path=(),
        cost=None,
        metrics=SearchMetrics(
            expanded_nodes=total_expanded,
            generated_nodes=total_generated,
            max_frontier_size=max_frontier_size,
            elapsed_seconds=perf_counter() - started_at,
            iterations=iterations,
        ),
    )


def _depth_limited_search(
    problem: SearchProblem[State], depth_limit: int
) -> _DepthLimitedResult[State]:
    frontier: list[tuple[State, ...]] = [(problem.start,)]
    best_depth: dict[State, int] = {problem.start: 0}
    expanded_nodes = 0
    generated_nodes = 1
    max_frontier_size = 1
    cutoff = False

    while frontier:
        path = frontier.pop()
        current = path[-1]
        current_depth = len(path) - 1
        if current_depth > best_depth[current]:
            continue
        if current == problem.goal:
            return _DepthLimitedResult(
                path,
                cutoff,
                expanded_nodes,
                generated_nodes,
                max_frontier_size,
            )

        expanded_nodes += 1
        path_states = set(path)
        next_depth = current_depth + 1
        eligible_neighbors = tuple(
            neighbor
            for neighbor in problem.neighbors(current)
            if neighbor not in path_states
            and next_depth < best_depth.get(neighbor, math.inf)
        )
        if current_depth == depth_limit:
            cutoff = cutoff or bool(eligible_neighbors)
            continue

        for neighbor in reversed(eligible_neighbors):
            best_depth[neighbor] = next_depth
            frontier.append((*path, neighbor))
            generated_nodes += 1
        max_frontier_size = max(max_frontier_size, len(frontier))

    return _DepthLimitedResult(
        None,
        cutoff,
        expanded_nodes,
        generated_nodes,
        max_frontier_size,
    )


def _resolve_depth_bound(
    problem: SearchProblem[State], max_depth: int | None
) -> int:
    if max_depth is not None:
        if type(max_depth) is not int:
            raise TypeError("max_depth must be an integer or None")
        if max_depth < 0:
            raise ValueError("max_depth cannot be negative")
        return max_depth

    traversable_count = getattr(problem, "traversable_count", None)
    if type(traversable_count) is not int or traversable_count < 1:
        raise ValueError(
            "max_depth is required when the problem has no traversable_count"
        )
    return traversable_count - 1


iddfs = iterative_deepening_search
