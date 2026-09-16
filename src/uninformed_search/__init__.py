"""Uninformed search algorithms for grid navigation."""

from uninformed_search.algorithms.bfs import bfs, breadth_first_search
from uninformed_search.algorithms.dfs import depth_first_search, dfs
from uninformed_search.algorithms.iterative_deepening import (
    iddfs,
    iterative_deepening_search,
)
from uninformed_search.algorithms.ucs import ucs, uniform_cost_search
from uninformed_search.comparison import (
    ALGORITHM_NAMES,
    compare_algorithms,
    format_results_table,
    run_algorithm,
)
from uninformed_search.grid import Coordinate, GridMap, generate_random_grid
from uninformed_search.models import SearchMetrics, SearchProblem, SearchResult

__all__ = [
    "ALGORITHM_NAMES",
    "Coordinate",
    "GridMap",
    "SearchMetrics",
    "SearchProblem",
    "SearchResult",
    "bfs",
    "breadth_first_search",
    "compare_algorithms",
    "depth_first_search",
    "dfs",
    "format_results_table",
    "generate_random_grid",
    "iddfs",
    "iterative_deepening_search",
    "run_algorithm",
    "ucs",
    "uniform_cost_search",
]
__version__ = "1.0.0"
