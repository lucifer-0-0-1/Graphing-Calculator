"""Unit tests for the Casio equation solver."""
import unittest
from src.casio.equation_solver import EquationSolver


class TestEquationSolver(unittest.TestCase):
    def test_quadratic_real_roots(self):
        # x² - 5x + 6 = 0 -> roots 2, 3
        res = EquationSolver.solve_quadratic(1, -5, 6)
        self.assertEqual(res["type"], "quadratic")
        self.assertIn("2", res["roots"])
        self.assertIn("3", res["roots"])
        self.assertEqual(res["discriminant"], 1)

    def test_quadratic_complex_roots(self):
        # x² + 1 = 0 -> ±i
        res = EquationSolver.solve_quadratic(1, 0, 1)
        self.assertEqual(res["type"], "quadratic")
        self.assertIn("Complex", res["nature"])

    def test_linear_2x2_system(self):
        # 2x + y = 5, x - y = 1 -> x=2, y=1
        res = EquationSolver.solve_linear_2x2(2, 1, 5, 1, -1, 1)
        self.assertEqual(res["x"], "2")
        self.assertEqual(res["y"], "1")


if __name__ == "__main__":
    unittest.main()
