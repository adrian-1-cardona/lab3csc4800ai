"""Run the grid navigation search lab from the command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

# This keeps ``python3 main.py`` simple while the package stays in src/.
project_folder = Path(__file__).resolve().parent
sys.path.insert(0, str(project_folder / "src"))

from uninformed_search import (  # noqa: E402
    ALGORITHM_NAMES,
    compare_algorithms,
    format_results_table,
    generate_random_grid,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line options for the navigation demo."""

    parser = argparse.ArgumentParser(
        description="compare uninformed search algorithms on a random grid"
    )
    parser.add_argument(
        "--algorithm",
        choices=("all", *ALGORITHM_NAMES),
        default="all",
        help="search algorithm to run (default: all)",
    )
    parser.add_argument("--rows", type=int, default=8, help="number of grid rows")
    parser.add_argument(
        "--cols", type=int, default=8, help="number of grid columns"
    )
    parser.add_argument(
        "--obstacles",
        type=float,
        default=0.2,
        help="chance that a cell is blocked, from 0 to 1",
    )
    parser.add_argument(
        "--min-weight",
        type=int,
        default=1,
        help="lowest cell travel cost",
    )
    parser.add_argument(
        "--max-weight",
        type=int,
        default=9,
        help="highest cell travel cost",
    )
    parser.add_argument(
        "--seed", type=int, default=4800, help="random seed for repeatable maps"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="optional depth limit for iterative deepening",
    )
    parser.add_argument(
        "--allow-unsolvable",
        action="store_true",
        help="do not protect a route between the start and goal",
    )
    parser.add_argument(
        "--hide-paths",
        action="store_true",
        help="only print the map and comparison table",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Generate one map, run the selected searches, and print the results."""

    parser = build_parser()
    options = parser.parse_args(arguments)

    try:
        grid = generate_random_grid(
            options.rows,
            options.cols,
            obstacle_rate=options.obstacles,
            min_weight=options.min_weight,
            max_weight=options.max_weight,
            seed=options.seed,
            ensure_solvable=not options.allow_unsolvable,
        )
        names = ALGORITHM_NAMES if options.algorithm == "all" else (options.algorithm,)
        results = compare_algorithms(grid, names, max_depth=options.max_depth)
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print("map")
    print(grid.render())
    print("\nlegend: S = start, G = goal, # = blocked, numbers = travel cost")
    print("\nresults")
    print(format_results_table(results))

    if not options.hide_paths:
        for result in results:
            print(f"\n{result.algorithm.lower()} path")
            if result.found:
                print(grid.render(result.path))
            else:
                print("no path found")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
