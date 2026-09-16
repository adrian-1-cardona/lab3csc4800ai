"""Depth-first search implementation."""

from __future__ import annotations

from time import perf_counter
from typing import Hashable, TypeVar

from uninformed_search.models import (
    SearchMetrics,
    SearchProblem,
    SearchResult,
    calculate_path_cost,
    reconstruct_path,
)

State = TypeVar("State", bound=Hashable)


def depth_first_search(problem: SearchProblem[State]) -> SearchResult[State]:
    """Find a path by following one branch at a time with a LIFO frontier."""

    started_at = perf_counter()
    frontier = [problem.start]
    discovered = {problem.start}
    parents: dict[State, State | None] = {problem.start: None}
    expanded_nodes = 0
    generated_nodes = 1
    max_frontier_size = 1

    while frontier:
        current = frontier.pop()
        if current == problem.goal:
            path = reconstruct_path(parents, current)
            return SearchResult(
                algorithm="DFS",
                found=True,
                path=path,
                cost=calculate_path_cost(problem, path),
                metrics=SearchMetrics(
                    expanded_nodes=expanded_nodes,
                    generated_nodes=generated_nodes,
                    max_frontier_size=max_frontier_size,
                    elapsed_seconds=perf_counter() - started_at,
                ),
            )

        expanded_nodes += 1
        neighbors = tuple(problem.neighbors(current))
        for neighbor in reversed(neighbors):
            if neighbor in discovered:
                continue
            discovered.add(neighbor)
            parents[neighbor] = current
            frontier.append(neighbor)
            generated_nodes += 1
        max_frontier_size = max(max_frontier_size, len(frontier))

    return SearchResult(
        algorithm="DFS",
        found=False,
        path=(),
        cost=None,
        metrics=SearchMetrics(
            expanded_nodes=expanded_nodes,
            generated_nodes=generated_nodes,
            max_frontier_size=max_frontier_size,
            elapsed_seconds=perf_counter() - started_at,
        ),
    )


dfs = depth_first_search
