"""Uniform-cost search implementation."""

from __future__ import annotations

import math
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Hashable, TypeVar

from uninformed_search.models import (
    SearchMetrics,
    SearchProblem,
    SearchResult,
    reconstruct_path,
)

State = TypeVar("State", bound=Hashable)


def uniform_cost_search(problem: SearchProblem[State]) -> SearchResult[State]:
    """Find a least-cost path using cumulative cost as the priority."""

    started_at = perf_counter()
    order = count()
    frontier: list[tuple[float, int, State]] = [
        (0.0, next(order), problem.start)
    ]
    best_cost: dict[State, float] = {problem.start: 0.0}
    parents: dict[State, State | None] = {problem.start: None}
    expanded_nodes = 0
    generated_nodes = 1
    max_frontier_size = 1

    while frontier:
        current_cost, _, current = heappop(frontier)
        if current_cost > best_cost[current]:
            continue
        if current == problem.goal:
            path = reconstruct_path(parents, current)
            return SearchResult(
                algorithm="UCS",
                found=True,
                path=path,
                cost=current_cost,
                metrics=SearchMetrics(
                    expanded_nodes=expanded_nodes,
                    generated_nodes=generated_nodes,
                    max_frontier_size=max_frontier_size,
                    elapsed_seconds=perf_counter() - started_at,
                ),
            )

        expanded_nodes += 1
        for neighbor in problem.neighbors(current):
            step_cost = problem.step_cost(current, neighbor)
            if not math.isfinite(step_cost) or step_cost < 0:
                raise ValueError("uniform-cost search requires finite nonnegative costs")
            candidate_cost = current_cost + step_cost
            if candidate_cost >= best_cost.get(neighbor, math.inf):
                continue
            best_cost[neighbor] = candidate_cost
            parents[neighbor] = current
            heappush(frontier, (candidate_cost, next(order), neighbor))
            generated_nodes += 1
        max_frontier_size = max(max_frontier_size, len(frontier))

    return SearchResult(
        algorithm="UCS",
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


ucs = uniform_cost_search
