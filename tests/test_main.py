"""Tests for the main command-line program."""

from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import main as program


class MainProgramTests(unittest.TestCase):
    def run_main(self, *arguments: str) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = program.main(arguments)
        return exit_code, output.getvalue()

    def test_main_compares_all_algorithms(self) -> None:
        exit_code, output = self.run_main(
            "--rows",
            "4",
            "--cols",
            "5",
            "--seed",
            "12",
            "--hide-paths",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("map\n", output)
        self.assertIn("results\n", output)
        for name in ("BFS", "DFS", "UCS", "IDDFS"):
            self.assertIn(name, output)
        self.assertNotIn("bfs path", output)

    def test_main_can_run_one_algorithm_and_show_its_path(self) -> None:
        exit_code, output = self.run_main(
            "--algorithm",
            "ucs",
            "--rows",
            "3",
            "--cols",
            "4",
            "--seed",
            "7",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("UCS", output)
        self.assertNotIn("BFS", output)
        self.assertIn("ucs path", output)
        self.assertIn("*", output)

    def test_main_reports_when_a_depth_limit_is_too_small(self) -> None:
        exit_code, output = self.run_main(
            "--algorithm",
            "iddfs",
            "--rows",
            "3",
            "--cols",
            "3",
            "--obstacles",
            "0",
            "--max-depth",
            "2",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("IDDFS", output)
        self.assertIn("no path found", output)

    def test_main_can_generate_an_unreachable_map(self) -> None:
        exit_code, output = self.run_main(
            "--rows",
            "2",
            "--cols",
            "2",
            "--obstacles",
            "1",
            "--allow-unsolvable",
            "--hide-paths",
        )

        self.assertEqual(exit_code, 0)
        result_lines = [line for line in output.splitlines() if "| no" in line]
        self.assertEqual(len(result_lines), 4)

    def test_main_rejects_invalid_grid_options_without_a_traceback(self) -> None:
        errors = StringIO()

        with redirect_stderr(errors):
            with self.assertRaises(SystemExit) as raised:
                program.main(("--rows", "0"))

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("rows and columns must be at least 1", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    def test_parser_rejects_an_unknown_algorithm(self) -> None:
        errors = StringIO()

        with redirect_stderr(errors):
            with self.assertRaises(SystemExit) as raised:
                program.main(("--algorithm", "random"))

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("invalid choice", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
