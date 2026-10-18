"""Unit tests for Desmos curve evaluation and numerical analysis."""
import unittest
import numpy as np
from src.desmos.analysis import CurveAnalyzer


class TestDesmosAnalysis(unittest.TestCase):
    def test_root_finding(self):
        # f(x) = x² - 4 in [-4, 4] -> roots -2 and 2
        f = lambda x: x**2 - 4
        roots = CurveAnalyzer.find_roots(f, -4, 4)
        self.assertEqual(len(roots), 2)
        self.assertAlmostEqual(roots[0], -2.0, places=3)
        self.assertAlmostEqual(roots[1], 2.0, places=3)

    def test_extrema_finding(self):
        # f(x) = -x² + 4 has local maximum at (0, 4)
        f = lambda x: -x**2 + 4
        extrema = CurveAnalyzer.find_extrema(f, -3, 3)
        self.assertTrue(any(t == "max" and abs(x) < 0.05 and abs(y - 4.0) < 0.05 for x, y, t in extrema))

    def test_numerical_integration(self):
        # ∫_0^2 x dx = 2.0
        f = lambda x: x
        area = CurveAnalyzer.integrate_area(f, 0, 2)
        self.assertAlmostEqual(area, 2.0, places=3)


if __name__ == "__main__":
    unittest.main()
