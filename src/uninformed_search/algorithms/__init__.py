"""Implementations of the uninformed search algorithms."""

from uninformed_search.algorithms.bfs import bfs, breadth_first_search
from uninformed_search.algorithms.dfs import depth_first_search, dfs
from uninformed_search.algorithms.iterative_deepening import (
    iddfs,
    iterative_deepening_search,
)
from uninformed_search.algorithms.ucs import ucs, uniform_cost_search

__all__ = [
    "bfs",
    "breadth_first_search",
    "depth_first_search",
    "dfs",
    "iddfs",
    "iterative_deepening_search",
    "ucs",
    "uniform_cost_search",
]
