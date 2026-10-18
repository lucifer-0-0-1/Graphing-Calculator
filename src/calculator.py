"""Core calculator logic and calculation engine."""
import math
from typing import Optional, Tuple


class CalculatorEngine:
    """Handles calculator state and arithmetic operations."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset calculator to initial state."""
        self.current_input: str = "0"
        self.previous_value: Optional[float] = None
        self.pending_operator: Optional[str] = None
        self.history_text: str = ""
        self.is_new_input: bool = True
        self.error_state: bool = False

    def clear(self) -> None:
        """All-clear (AC)."""
        self.reset()

    def clear_entry(self) -> None:
        """Clear only current entry (CE)."""
        if self.error_state:
            self.reset()
        else:
            self.current_input = "0"
            self.is_new_input = True

    def input_digit(self, digit: str) -> None:
        """Append digit to current input."""
        if self.error_state:
            self.reset()

        if self.is_new_input:
            self.current_input = digit
            self.is_new_input = False
        else:
            if self.current_input == "0":
                self.current_input = digit
            else:
                if len(self.current_input) < 16:  # limit input length
                    self.current_input += digit

    def input_decimal(self) -> None:
        """Append decimal point to current input."""
        if self.error_state:
            self.reset()

        if self.is_new_input:
            self.current_input = "0."
            self.is_new_input = False
        elif "." not in self.current_input:
            self.current_input += "."

    def backspace(self) -> None:
        """Delete last character from current input."""
        if self.error_state or self.is_new_input:
            return

        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
            if self.current_input == "-" or self.current_input == "":
                self.current_input = "0"
                self.is_new_input = True
        else:
            self.current_input = "0"
            self.is_new_input = True

    def toggle_sign(self) -> None:
        """Toggle positive/negative sign."""
        if self.error_state:
            return

        if self.current_input == "0":
            return

        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input

    def apply_unary_op(self, op: str) -> Tuple[bool, str]:
        """Apply unary operations such as sqrt, square, reciprocal, percent."""
        if self.error_state:
            return False, "Error"

        try:
            val = float(self.current_input)
            result: float = 0.0

            if op == "sqrt":
                if val < 0:
                    self.error_state = True
                    self.current_input = "Invalid input"
                    return False, "Invalid input"
                result = math.sqrt(val)
                self.history_text = f"√({self._format_number(val)})"
            elif op == "square":
                result = val ** 2
                self.history_text = f"sqr({self._format_number(val)})"
            elif op == "reciprocal":
                if val == 0:
                    self.error_state = True
                    self.current_input = "Cannot divide by zero"
                    return False, "Cannot divide by zero"
                result = 1.0 / val
                self.history_text = f"1/({self._format_number(val)})"
            elif op == "percent":
                if self.previous_value is not None and self.pending_operator in ("+", "-"):
                    result = self.previous_value * (val / 100.0)
                else:
                    result = val / 100.0
                self.history_text = f"{self._format_number(val)}%"
            else:
                return False, "Unknown op"

            formatted = self._format_number(result)
            self.current_input = formatted
            self.is_new_input = True
            return True, formatted
        except OverflowError:
            self.error_state = True
            self.current_input = "Overflow"
            return False, "Overflow"
        except Exception:
            self.error_state = True
            self.current_input = "Error"
            return False, "Error"

    def apply_binary_op(self, op: str) -> None:
        """Apply binary operator (+, -, ×, ÷, ^)."""
        if self.error_state:
            self.reset()

        val = float(self.current_input)

        if self.previous_value is not None and not self.is_new_input:
            self.calculate()
            val = float(self.current_input)

        self.previous_value = val
        self.pending_operator = op
        self.history_text = f"{self._format_number(val)} {op}"
        self.is_new_input = True

    def calculate(self) -> None:
        """Perform evaluation when '=' is pressed."""
        if self.error_state:
            return

        if self.previous_value is None or self.pending_operator is None:
            return

        try:
            prev = self.previous_value
            curr = float(self.current_input)
            op = self.pending_operator
            result: float = 0.0

            if op == "+":
                result = prev + curr
            elif op == "-":
                result = prev - curr
            elif op in ("*", "×"):
                result = prev * curr
            elif op in ("/", "÷"):
                if curr == 0:
                    self.error_state = True
                    self.current_input = "Cannot divide by zero"
                    self.history_text = f"{self._format_number(prev)} {op} 0 ="
                    self.previous_value = None
                    self.pending_operator = None
                    self.is_new_input = True
                    return
                result = prev / curr
            elif op == "^":
                result = prev ** curr
            else:
                return

            self.history_text = f"{self._format_number(prev)} {op} {self._format_number(curr)} ="
            formatted = self._format_number(result)
            self.current_input = formatted
            self.previous_value = None
            self.pending_operator = None
            self.is_new_input = True
        except OverflowError:
            self.error_state = True
            self.current_input = "Overflow"
            self.previous_value = None
            self.pending_operator = None
            self.is_new_input = True
        except Exception:
            self.error_state = True
            self.current_input = "Error"
            self.previous_value = None
            self.pending_operator = None
            self.is_new_input = True

    @staticmethod
    def _format_number(val: float) -> str:
        """Format a floating point number cleanly."""
        if math.isinf(val):
            return "Overflow"
        if math.isnan(val):
            return "Error"

        # Round very small floating point noise (e.g. 0.1 + 0.2 = 0.30000000000000004)
        rounded = round(val, 10)
        if rounded.is_integer():
            return str(int(rounded))

        # Scientific notation for very large or tiny numbers
        abs_val = abs(rounded)
        if (abs_val >= 1e12 or abs_val < 1e-6) and abs_val != 0:
            formatted = f"{val:.6e}"
            return formatted

        s = f"{rounded:.10f}".rstrip("0").rstrip(".")
        return s
