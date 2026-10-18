"""Unit tests for Casio fx-991CW Symbolic and Scientific Engine."""
import unittest
import math
from src.casio.casio_engine import CasioEngine


class TestCasioEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CasioEngine()

    def test_exact_fractions(self):
        ok, res, _ = self.engine.evaluate("1/3 + 1/6")
        self.assertTrue(ok)
        self.assertEqual(res, "1/2")

    def test_surd_radicals(self):
        ok, res, _ = self.engine.evaluate("√(12)")
        self.assertTrue(ok)
        self.assertIn("3", res)

    def test_sd_toggle(self):
        self.engine.evaluate("1/2")
        self.assertEqual(self.engine.get_formatted_result(), "1/2")
        dec = self.engine.toggle_exact_decimal()
        self.assertEqual(dec, "0.5")
        exact = self.engine.toggle_exact_decimal()
        self.assertEqual(exact, "1/2")

    def test_trig_deg_mode(self):
        self.engine.set_angle_mode("DEG")
        ok, res, _ = self.engine.evaluate("sin(30)")
        self.assertTrue(ok)
        self.assertEqual(res, "1/2")

    def test_trig_rad_mode(self):
        self.engine.set_angle_mode("RAD")
        ok, res, _ = self.engine.evaluate("sin(pi/6)")
        self.assertTrue(ok)
        self.assertEqual(res, "1/2")

    def test_combinatorics(self):
        ok, res, _ = self.engine.evaluate("5!")
        self.assertTrue(ok)
        self.assertEqual(res, "120")

        ok, res, _ = self.engine.evaluate("5nCr2")
        self.assertTrue(ok)
        self.assertEqual(res, "10")

        ok, res, _ = self.engine.evaluate("5nPr2")
        self.assertTrue(ok)
        self.assertEqual(res, "20")

    def test_derivative(self):
        ok, res = self.engine.evaluate_derivative("x^3 - 2*x", 2.0)
        self.assertTrue(ok)
        self.assertEqual(float(res), 10.0)

    def test_definite_integral(self):
        ok, res = self.engine.evaluate_integral("sin(x)", 0.0, math.pi)
        self.assertTrue(ok)
        self.assertAlmostEqual(float(res), 2.0, places=4)

    def test_constants(self):
        ok, res, _ = self.engine.evaluate("c")
        self.assertTrue(ok)
        self.assertEqual(res, "299792458")


if __name__ == "__main__":
    unittest.main()
