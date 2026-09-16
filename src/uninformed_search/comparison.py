"""Utilities for running and comparing all search algorithms fairly."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Hashable, TypeVar

from uninformed_search.algorithms.bfs import breadth_first_search
from uninformed_search.algorithms.dfs import depth_first_search
from uninformed_search.algorithms.iterative_deepening import (
    iterative_deepening_search,
)
from uninformed_search.algorithms.ucs import uniform_cost_search
from uninformed_search.models import SearchProblem, SearchResult

State = TypeVar("State", bound=Hashable)
ALGORITHM_NAMES = ("bfs", "dfs", "ucs", "iddfs")


def run_algorithm(
    problem: SearchProblem[State],
    algorithm: str,
    *,
    max_depth: int | None = None,
) -> SearchResult[State]:
    """Run one named algorithm against a search problem."""

    normalized_name = algorithm.strip().lower()
    if normalized_name == "bfs":
        return breadth_first_search(problem)
    if normalized_name == "dfs":
        return depth_first_search(problem)
    if normalized_name == "ucs":
        return uniform_cost_search(problem)
    if normalized_name == "iddfs":
        return iterative_deepening_search(problem, max_depth=max_depth)
    choices = ", ".join(ALGORITHM_NAMES)
    raise ValueError(f"unknown algorithm {algorithm!r}; choose from {choices}")


def compare_algorithms(
    problem: SearchProblem[State],
    algorithms: Iterable[str] = ALGORITHM_NAMES,
    *,
    max_depth: int | None = None,
) -> tuple[SearchResult[State], ...]:
    """Run selected algorithms in order on the same problem instance."""

    selected = tuple(algorithms)
    if not selected:
        raise ValueError("at least one algorithm must be selected")
    return tuple(
        run_algorithm(problem, algorithm, max_depth=max_depth)
        for algorithm in selected
    )


def format_results_table(results: Sequence[SearchResult[object]]) -> str:
    """Format search outcomes and performance measurements as a table."""

    if not results:
        raise ValueError("at least one result is required")

    headers = (
        "algorithm",
        "found",
        "depth",
        "cost",
        "expanded",
        "generated",
        "max frontier",
        "iterations",
        "time (ms)",
    )
    rows = [
        (
            result.algorithm,
            "yes" if result.found else "no",
            _display_optional(result.depth),
            _display_cost(result.cost),
            str(result.metrics.expanded_nodes),
            str(result.metrics.generated_nodes),
            str(result.metrics.max_frontier_size),
            str(result.metrics.iterations),
            f"{result.metrics.elapsed_seconds * 1000:.3f}",
        )
        for result in results
    ]
    widths = tuple(
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    )
    header_line = " | ".join(
        value.ljust(widths[index]) for index, value in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in widths)
    body = [
        " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        )
        for row in rows
    ]
    return "\n".join((header_line, separator, *body))


def _display_optional(value: int | None) -> str:
    return "-" if value is None else str(value)


def _display_cost(value: float | None) -> str:
    if value is None:
        return "-"
    if value.is_integer():
        return str(int(value))
    return f"{value:.3f}"
