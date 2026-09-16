"""Uninformed search algorithms for grid navigation."""

from uninformed_search.algorithms.bfs import bfs, breadth_first_search
from uninformed_search.grid import Coordinate, GridMap, generate_random_grid
from uninformed_search.models import SearchMetrics, SearchProblem, SearchResult

__all__ = [
    "Coordinate",
    "GridMap",
    "SearchMetrics",
    "SearchProblem",
    "SearchResult",
    "bfs",
    "breadth_first_search",
    "generate_random_grid",
]
__version__ = "1.0.0"
