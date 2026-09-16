"""Uninformed search algorithms for grid navigation."""

from uninformed_search.grid import Coordinate, GridMap, generate_random_grid
from uninformed_search.models import SearchMetrics, SearchProblem, SearchResult

__all__ = [
    "Coordinate",
    "GridMap",
    "SearchMetrics",
    "SearchProblem",
    "SearchResult",
    "generate_random_grid",
]
__version__ = "1.0.0"
