"""Tests for grid creation, validation, and display."""

from __future__ import annotations

import random
import unittest

from uninformed_search import GridMap, bfs, generate_random_grid


class GridMapTests(unittest.TestCase):
    def test_uniform_grid_uses_the_requested_values(self) -> None:
        grid = GridMap.uniform(
            3,
            4,
            start=(0, 1),
            goal=(2, 2),
            blocked={(1, 1)},
            weight=3,
        )

        self.assertEqual(grid.rows, 3)
        self.assertEqual(grid.columns, 4)
        self.assertEqual(grid.start, (0, 1))
        self.assertEqual(grid.goal, (2, 2))
        self.assertEqual(grid.weights[2][3], 3)
        self.assertEqual(grid.traversable_count, 11)

    def test_neighbors_have_a_repeatable_order(self) -> None:
        grid = GridMap.uniform(3, 3)

        self.assertEqual(
            grid.neighbors((1, 1)),
            ((0, 1), (1, 2), (2, 1), (1, 0)),
        )
        self.assertEqual(grid.neighbors((0, 0)), ((0, 1), (1, 0)))

    def test_neighbors_skip_blocked_cells(self) -> None:
        grid = GridMap.uniform(3, 3, blocked={(0, 1), (1, 0)})

        self.assertEqual(grid.neighbors((0, 0)), ())
        with self.assertRaises(ValueError):
            grid.neighbors((0, 1))

    def test_step_cost_comes_from_the_destination_cell(self) -> None:
        grid = GridMap(
            2,
            2,
            (0, 0),
            (1, 1),
            frozenset(),
            ((1, 7), (3, 2)),
        )

        self.assertEqual(grid.step_cost((0, 0), (0, 1)), 7.0)
        self.assertEqual(grid.step_cost((0, 0), (1, 0)), 3.0)
        with self.assertRaises(ValueError):
            grid.step_cost((0, 0), (1, 1))

    def test_path_validation_checks_start_goal_and_each_move(self) -> None:
        grid = GridMap.uniform(2, 3)
        valid_path = ((0, 0), (0, 1), (0, 2), (1, 2))

        self.assertTrue(grid.is_valid_path(valid_path))
        self.assertFalse(grid.is_valid_path(()))
        self.assertFalse(grid.is_valid_path(((0, 1), (0, 2), (1, 2))))
        self.assertFalse(grid.is_valid_path(((0, 0), (1, 2))))

    def test_render_marks_the_map_and_path(self) -> None:
        grid = GridMap(
            2,
            3,
            (0, 0),
            (0, 2),
            frozenset({(1, 0)}),
            ((1, 2, 3), (4, 5, 6)),
        )

        self.assertEqual(grid.render(((0, 0), (0, 1), (0, 2))), "S * G\n# 5 6")

    def test_grid_rejects_invalid_dimensions_and_weights(self) -> None:
        with self.assertRaises(ValueError):
            GridMap.uniform(0, 3)
        with self.assertRaises(TypeError):
            GridMap.uniform(True, 3)
        with self.assertRaises(ValueError):
            GridMap(2, 2, (0, 0), (1, 1), frozenset(), ((1, 1),))
        with self.assertRaises(ValueError):
            GridMap(2, 2, (0, 0), (1, 1), frozenset(), ((1, 1), (1, 0)))

    def test_grid_rejects_invalid_endpoints_and_blocks(self) -> None:
        with self.assertRaises(ValueError):
            GridMap.uniform(2, 2, start=(-1, 0))
        with self.assertRaises(ValueError):
            GridMap.uniform(2, 2, goal=(2, 1))
        with self.assertRaises(ValueError):
            GridMap.uniform(2, 2, blocked={(0, 0)})
        with self.assertRaises(ValueError):
            GridMap.uniform(2, 2, blocked={(4, 4)})

    def test_seeded_generation_is_repeatable(self) -> None:
        first = generate_random_grid(8, 7, seed=25)
        second = generate_random_grid(8, 7, seed=25)

        self.assertEqual(first, second)

    def test_generated_weights_stay_inside_the_bounds(self) -> None:
        grid = generate_random_grid(7, 6, min_weight=3, max_weight=5, seed=6)

        self.assertTrue(
            all(3 <= weight <= 5 for row in grid.weights for weight in row)
        )

    def test_solvable_generation_protects_a_route(self) -> None:
        grid = generate_random_grid(6, 7, obstacle_rate=1.0, seed=10)

        result = bfs(grid)

        self.assertTrue(result.found)
        self.assertTrue(grid.is_valid_path(result.path))

    def test_generation_can_make_an_unsolvable_map(self) -> None:
        grid = generate_random_grid(
            3,
            3,
            obstacle_rate=1.0,
            seed=10,
            ensure_solvable=False,
        )

        self.assertFalse(bfs(grid).found)
        self.assertNotIn(grid.start, grid.blocked)
        self.assertNotIn(grid.goal, grid.blocked)

    def test_generation_supports_custom_endpoints(self) -> None:
        grid = generate_random_grid(
            5,
            6,
            start=(4, 0),
            goal=(0, 5),
            obstacle_rate=0.9,
            seed=2,
        )

        self.assertEqual(grid.start, (4, 0))
        self.assertEqual(grid.goal, (0, 5))
        self.assertTrue(bfs(grid).found)

    def test_generation_does_not_change_the_global_random_state(self) -> None:
        random.seed(1234)
        expected_next_value = random.random()
        random.seed(1234)

        generate_random_grid(5, 5, seed=99)
        actual_next_value = random.random()

        self.assertEqual(actual_next_value, expected_next_value)

    def test_generation_rejects_invalid_options(self) -> None:
        invalid_options = (
            {"obstacle_rate": -0.1},
            {"obstacle_rate": 1.1},
            {"min_weight": 0},
            {"min_weight": 5, "max_weight": 4},
            {"seed": True},
            {"ensure_solvable": 1},
        )

        for options in invalid_options:
            with self.subTest(options=options):
                with self.assertRaises((TypeError, ValueError)):
                    generate_random_grid(3, 3, **options)


if __name__ == "__main__":
    unittest.main()
