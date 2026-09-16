"""Tests for the four uninformed search algorithms."""

from __future__ import annotations

import math
import unittest

from uninformed_search import (
    GridMap,
    SearchMetrics,
    SearchResult,
    bfs,
    compare_algorithms,
    dfs,
    format_results_table,
    iddfs,
    run_algorithm,
    ucs,
)


class SimpleGraph:
    """Small graph used to test costs that are not tied to a grid."""

    def __init__(
        self,
        edges: dict[str, tuple[tuple[str, float], ...]],
        start: str = "A",
        goal: str = "G",
    ) -> None:
        self.edges = edges
        self.start = start
        self.goal = goal

    def neighbors(self, state: str) -> tuple[str, ...]:
        return tuple(neighbor for neighbor, _ in self.edges.get(state, ()))

    def step_cost(self, current: str, neighbor: str) -> float:
        for next_state, cost in self.edges.get(current, ()):
            if next_state == neighbor:
                return cost
        raise ValueError("the states are not connected")


class SearchAlgorithmTests(unittest.TestCase):
    def setUp(self) -> None:
        self.weighted_grid = GridMap(
            rows=2,
            columns=3,
            start=(0, 0),
            goal=(0, 2),
            blocked=frozenset(),
            weights=((1, 9, 1), (1, 1, 1)),
        )

    def test_bfs_finds_the_path_with_fewest_moves(self) -> None:
        result = bfs(self.weighted_grid)

        self.assertTrue(result.found)
        self.assertEqual(result.depth, 2)
        self.assertEqual(result.cost, 10.0)
        self.assertTrue(self.weighted_grid.is_valid_path(result.path))

    def test_dfs_finds_a_valid_path_without_cycles(self) -> None:
        result = dfs(GridMap.uniform(5, 5))

        self.assertTrue(result.found)
        self.assertTrue(GridMap.uniform(5, 5).is_valid_path(result.path))
        self.assertEqual(len(result.path), len(set(result.path)))

    def test_ucs_finds_the_path_with_lowest_cost(self) -> None:
        result = ucs(self.weighted_grid)

        self.assertTrue(result.found)
        self.assertEqual(result.depth, 4)
        self.assertEqual(result.cost, 4.0)
        self.assertTrue(self.weighted_grid.is_valid_path(result.path))

    def test_ucs_replaces_a_more_expensive_route(self) -> None:
        graph = SimpleGraph(
            {
                "A": (("B", 10.0), ("C", 1.0)),
                "B": (("G", 1.0),),
                "C": (("B", 1.0), ("G", 100.0)),
                "G": (),
            }
        )

        result = ucs(graph)

        self.assertEqual(result.path, ("A", "C", "B", "G"))
        self.assertEqual(result.cost, 3.0)

    def test_ucs_rejects_negative_and_infinite_costs(self) -> None:
        for bad_cost in (-1.0, math.inf):
            graph = SimpleGraph({"A": (("G", bad_cost),), "G": ()})
            with self.subTest(cost=bad_cost):
                with self.assertRaises(ValueError):
                    ucs(graph)

    def test_iddfs_finds_the_same_depth_as_bfs(self) -> None:
        grid = GridMap.uniform(4, 5, blocked={(1, 1), (1, 2), (2, 2)})

        breadth_result = bfs(grid)
        deepening_result = iddfs(grid)

        self.assertTrue(deepening_result.found)
        self.assertEqual(deepening_result.depth, breadth_result.depth)
        self.assertEqual(
            deepening_result.metrics.iterations,
            deepening_result.depth + 1,
        )
        self.assertTrue(grid.is_valid_path(deepening_result.path))

    def test_iddfs_respects_the_depth_limit(self) -> None:
        grid = GridMap.uniform(3, 3)

        failed = iddfs(grid, max_depth=3)
        found = iddfs(grid, max_depth=4)

        self.assertFalse(failed.found)
        self.assertTrue(found.found)
        self.assertEqual(found.depth, 4)

    def test_iddfs_needs_a_bound_for_a_generic_graph(self) -> None:
        graph = SimpleGraph({"A": (("G", 1.0),), "G": ()})

        with self.assertRaises(ValueError):
            iddfs(graph)
        self.assertTrue(iddfs(graph, max_depth=1).found)

    def test_iddfs_reopens_a_state_found_at_a_shallower_depth(self) -> None:
        graph = SimpleGraph(
            {
                "A": (("B", 1.0), ("C", 1.0)),
                "B": (("D", 1.0),),
                "C": (("X", 1.0),),
                "D": (("X", 1.0),),
                "X": (("G", 1.0),),
                "G": (),
            }
        )

        result = iddfs(graph, max_depth=3)

        self.assertTrue(result.found)
        self.assertEqual(result.path, ("A", "C", "X", "G"))
        self.assertEqual(result.depth, 3)

    def test_iddfs_stops_after_finishing_an_unreachable_cycle(self) -> None:
        graph = SimpleGraph(
            {
                "A": (("B", 1.0),),
                "B": (("A", 1.0),),
                "G": (),
            }
        )

        result = iddfs(graph, max_depth=10)

        self.assertFalse(result.found)
        self.assertEqual(result.metrics.iterations, 2)

    def test_all_algorithms_report_failure_on_an_unreachable_grid(self) -> None:
        grid = GridMap.uniform(2, 2, blocked={(0, 1), (1, 0)})

        for search in (bfs, dfs, ucs, iddfs):
            with self.subTest(algorithm=search.__name__):
                result = search(grid)
                self.assertFalse(result.found)
                self.assertEqual(result.path, ())
                self.assertIsNone(result.cost)
                self.assertIsNone(result.depth)

    def test_all_algorithms_handle_start_equal_to_goal(self) -> None:
        grid = GridMap.uniform(1, 1)

        for search in (bfs, dfs, ucs, iddfs):
            with self.subTest(algorithm=search.__name__):
                result = search(grid)
                self.assertEqual(result.path, ((0, 0),))
                self.assertEqual(result.depth, 0)
                self.assertEqual(result.cost, 0.0)
                self.assertIsInstance(result.cost, float)
                self.assertEqual(result.metrics.expanded_nodes, 0)
                self.assertEqual(result.metrics.generated_nodes, 1)
                self.assertEqual(result.metrics.max_frontier_size, 1)

        table = format_results_table(compare_algorithms(grid))
        self.assertIn("| 0", table)

    def test_metrics_are_present_for_every_algorithm(self) -> None:
        results = compare_algorithms(GridMap.uniform(3, 3))

        self.assertEqual(
            tuple(result.algorithm for result in results),
            ("BFS", "DFS", "UCS", "IDDFS"),
        )
        for result in results:
            self.assertGreaterEqual(result.metrics.expanded_nodes, 0)
            self.assertGreaterEqual(result.metrics.generated_nodes, 1)
            self.assertGreaterEqual(result.metrics.max_frontier_size, 1)
            self.assertGreaterEqual(result.metrics.elapsed_seconds, 0.0)

    def test_named_algorithm_runner_validates_the_name(self) -> None:
        grid = GridMap.uniform(2, 2)

        self.assertEqual(run_algorithm(grid, " BFS ").algorithm, "BFS")
        with self.assertRaises(ValueError):
            run_algorithm(grid, "best search")
        with self.assertRaises(ValueError):
            compare_algorithms(grid, ())

    def test_comparison_table_contains_every_measurement(self) -> None:
        results = compare_algorithms(GridMap.uniform(2, 2))

        table = format_results_table(results)

        for heading in (
            "algorithm",
            "found",
            "depth",
            "cost",
            "expanded",
            "generated",
            "max frontier",
            "iterations",
            "time (ms)",
        ):
            self.assertIn(heading, table)

    def test_result_classes_reject_inconsistent_values(self) -> None:
        metrics = SearchMetrics(0, 1, 1, 0.0)

        with self.assertRaises(ValueError):
            SearchMetrics(-1, 1, 1, 0.0)
        with self.assertRaises(ValueError):
            SearchResult("BFS", True, (), None, metrics)
        with self.assertRaises(ValueError):
            SearchResult("BFS", False, ((0, 0),), 0.0, metrics)


if __name__ == "__main__":
    unittest.main()
