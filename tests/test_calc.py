"""Unit tests for the calculator logic."""
import unittest
from src.calculator import CalculatorEngine


class TestCalculatorEngine(unittest.TestCase):
    def setUp(self):
        self.calc = CalculatorEngine()

    def test_initial_state(self):
        self.assertEqual(self.calc.current_input, "0")
        self.assertIsNone(self.calc.previous_value)
        self.assertIsNone(self.calc.pending_operator)

    def test_digit_input(self):
        self.calc.input_digit("7")
        self.assertEqual(self.calc.current_input, "7")
        self.calc.input_digit("5")
        self.assertEqual(self.calc.current_input, "75")

    def test_decimal_input(self):
        self.calc.input_digit("3")
        self.calc.input_decimal()
        self.calc.input_digit("1")
        self.calc.input_digit("4")
        self.assertEqual(self.calc.current_input, "3.14")
        # Duplicate decimal is ignored
        self.calc.input_decimal()
        self.assertEqual(self.calc.current_input, "3.14")

    def test_addition(self):
        self.calc.input_digit("1")
        self.calc.input_digit("5")
        self.calc.apply_binary_op("+")
        self.calc.input_digit("2")
        self.calc.input_digit("7")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "42")

    def test_subtraction_and_floats(self):
        self.calc.input_digit("0")
        self.calc.input_decimal()
        self.calc.input_digit("3")
        self.calc.apply_binary_op("-")
        self.calc.input_digit("0")
        self.calc.input_decimal()
        self.calc.input_digit("1")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "0.2")

    def test_multiplication(self):
        self.calc.input_digit("6")
        self.calc.apply_binary_op("×")
        self.calc.input_digit("7")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "42")

    def test_division(self):
        self.calc.input_digit("8")
        self.calc.input_digit("4")
        self.calc.apply_binary_op("÷")
        self.calc.input_digit("2")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "42")

    def test_division_by_zero(self):
        self.calc.input_digit("5")
        self.calc.apply_binary_op("÷")
        self.calc.input_digit("0")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "Cannot divide by zero")
        self.assertTrue(self.calc.error_state)

    def test_square_root(self):
        self.calc.input_digit("6")
        self.calc.input_digit("4")
        success, res = self.calc.apply_unary_op("sqrt")
        self.assertTrue(success)
        self.assertEqual(res, "8")
        self.assertEqual(self.calc.current_input, "8")

    def test_negative_square_root(self):
        self.calc.input_digit("9")
        self.calc.toggle_sign()
        success, res = self.calc.apply_unary_op("sqrt")
        self.assertFalse(success)
        self.assertEqual(res, "Invalid input")

    def test_square(self):
        self.calc.input_digit("1")
        self.calc.input_digit("2")
        success, res = self.calc.apply_unary_op("square")
        self.assertTrue(success)
        self.assertEqual(res, "144")

    def test_reciprocal(self):
        self.calc.input_digit("4")
        success, res = self.calc.apply_unary_op("reciprocal")
        self.assertTrue(success)
        self.assertEqual(res, "0.25")

    def test_backspace(self):
        self.calc.input_digit("1")
        self.calc.input_digit("2")
        self.calc.input_digit("3")
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "12")
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "1")
        self.calc.backspace()
        self.assertEqual(self.calc.current_input, "0")

    def test_chained_operations(self):
        # 5 + 3 * 2 = (5 + 3) = 8, then 8 * 2 = 16 (standard calculator behavior)
        self.calc.input_digit("5")
        self.calc.apply_binary_op("+")
        self.calc.input_digit("3")
        self.calc.apply_binary_op("×")
        self.assertEqual(self.calc.current_input, "8")
        self.calc.input_digit("2")
        self.calc.calculate()
        self.assertEqual(self.calc.current_input, "16")


if __name__ == "__main__":
    unittest.main()
