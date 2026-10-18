"""Casio fx-991CW Symbolic and Scientific Math Engine using SymPy."""
import math
import re
from typing import Tuple, Optional, Any, Dict
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)


class CasioEngine:
    """Symbolic and numerical calculation engine replicating Casio fx-991CW ClassWiz."""

    # Fundamental physical constants (CODATA standard)
    CONSTANTS: Dict[str, Tuple[Any, str]] = {
        "c": (299792458, "Speed of light (m/s)"),
        "h": (6.62607015e-34, "Planck constant (J·s)"),
        "G": (6.67430e-11, "Gravitational constant (m³/kg·s²)"),
        "N_A": (6.02214076e23, "Avogadro constant (mol⁻¹)"),
        "k_B": (1.380649e-23, "Boltzmann constant (J/K)"),
        "q_e": (1.602176634e-19, "Elementary charge (C)"),
        "m_e": (9.1093837015e-31, "Electron mass (kg)"),
        "m_p": (1.67262192369e-27, "Proton mass (kg)"),
        "R": (8.314462618, "Molar gas constant (J/mol·K)"),
        "g": (9.80665, "Standard gravity (m/s²)"),
    }

    def __init__(self):
        self.angle_mode: str = "DEG"  # "DEG", "RAD", "GRA"
        self.last_exact_result: Optional[sp.Expr] = None
        self.last_approx_result: Optional[str] = None
        self.display_as_decimal: bool = False
        self.ans_value: sp.Expr = sp.Integer(0)
        self.history: list[Tuple[str, str, str]] = []  # (expression, exact_str, approx_str)

        self._transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

    def set_angle_mode(self, mode: str) -> None:
        """Switch between DEG, RAD, and GRA."""
        if mode.upper() in ("DEG", "RAD", "GRA"):
            self.angle_mode = mode.upper()

    def toggle_exact_decimal(self) -> str:
        """Casio [S<=>D] toggle key between exact representation and decimal."""
        if self.last_exact_result is None:
            return "0"
        self.display_as_decimal = not self.display_as_decimal
        return self.get_formatted_result()

    def get_formatted_result(self) -> str:
        """Return the current result in either exact textbook format or decimal approximation."""
        if self.last_exact_result is None:
            return "0"

        if self.display_as_decimal:
            return self.last_approx_result or str(self.last_exact_result)
        else:
            # Pretty exact format
            return self._format_exact(self.last_exact_result)

    def evaluate(self, expr_str: str) -> Tuple[bool, str, str]:
        """
        Evaluate expression string using Casio fx-991CW logic.
        Returns: (success, display_string, detail_latex_or_text)
        """
        if not expr_str or not expr_str.strip():
            return True, "0", ""

        cleaned = self._preprocess_expression(expr_str)

        try:
            # Build local context with constants and angle-aware trig functions
            local_dict = self._build_context()

            parsed = parse_expr(
                cleaned,
                local_dict=local_dict,
                transformations=self._transformations,
                evaluate=True,
            )

            # Simplify exact expression
            exact = sp.simplify(parsed)
            self.last_exact_result = exact
            self.ans_value = exact

            # Calculate decimal representation (up to 12 significant digits like ClassWiz)
            try:
                approx_val = sp.N(exact, 12)
                if approx_val.is_real:
                    fval = float(approx_val)
                    if math.isnan(fval) or math.isinf(fval):
                        approx_str = str(fval)
                    elif fval.is_integer() and abs(fval) < 1e12:
                        approx_str = str(int(fval))
                    else:
                        approx_str = f"{fval:.10g}"
                else:
                    # Complex number
                    approx_str = str(approx_val)
            except Exception:
                approx_str = str(exact)

            self.last_approx_result = approx_str
            self.display_as_decimal = False  # Default to exact textbook display first

            out = self.get_formatted_result()
            self.history.append((expr_str, str(exact), approx_str))
            return True, out, str(exact)

        except ZeroDivisionError:
            return False, "Math ERROR: Division by Zero", ""
        except sp.PolynomialError as pe:
            return False, f"Polynomial ERROR: {pe}", ""
        except Exception as e:
            msg = str(e)
            if "syntax" in msg.lower() or "unexpected" in msg.lower():
                return False, "Syntax ERROR", ""
            return False, f"Math ERROR", ""

    def evaluate_derivative(self, expr_str: str, at_val: float) -> Tuple[bool, str]:
        """Compute numerical / symbolic derivative d/dx f(x) at x = at_val (in radians)."""
        try:
            x = sp.Symbol('x')
            local_dict = self._build_context(force_rad=True)
            parsed = parse_expr(self._preprocess_expression(expr_str), local_dict=local_dict, transformations=self._transformations)
            diff_expr = sp.diff(parsed, x)
            val = diff_expr.subs(x, at_val)
            res = sp.simplify(val)
            fres = float(sp.N(res, 10))
            return True, f"{fres:.8g}"
        except Exception as e:
            return False, "Derivative ERROR"

    def evaluate_integral(self, expr_str: str, a: float, b: float) -> Tuple[bool, str]:
        """Compute definite integral ∫_a^b f(x) dx (in radians)."""
        try:
            x = sp.Symbol('x')
            local_dict = self._build_context(force_rad=True)
            parsed = parse_expr(self._preprocess_expression(expr_str), local_dict=local_dict, transformations=self._transformations)
            res = sp.integrate(parsed, (x, a, b))
            fres = float(sp.N(res, 10))
            return True, f"{fres:.8g}"
        except Exception as e:
            return False, "Integral ERROR"

    def generate_table(self, expr_str: str, start: float, end: float, step: float) -> list[Tuple[float, str]]:
        """Generate function table f(x) across [start, end] with given step."""
        table = []
        if step <= 0:
            step = 1.0

        try:
            x = sp.Symbol('x')
            local_dict = self._build_context()
            parsed = parse_expr(self._preprocess_expression(expr_str), local_dict=local_dict, transformations=self._transformations)
            curr = start
            max_rows = 100
            count = 0
            while curr <= end + 1e-9 and count < max_rows:
                val = parsed.subs(x, curr)
                try:
                    fval = float(sp.N(val, 8))
                    val_str = f"{fval:.6g}"
                except Exception:
                    val_str = "ERROR"
                table.append((round(curr, 6), val_str))
                curr += step
                count += 1
        except Exception:
            pass

        return table

    def _preprocess_expression(self, s: str) -> str:
        """Format Casio keypad characters into standard SymPy syntax."""
        s = s.replace("×", "*").replace("÷", "/").replace("−", "-")
        s = s.replace("π", "pi").replace("Ans", "ans")
        s = s.replace("√", "sqrt")

        # Handle nth root: root(x, n)
        # Handle nCr and nPr functions
        s = re.sub(r'(\d+)nCr(\d+)', r'binomial(\1, \2)', s)
        s = re.sub(r'(\d+)nPr(\d+)', r'(factorial(\1)/factorial(\1-\2))', s)

        # Factorial symbol 5! -> factorial(5)
        s = re.sub(r'(\w+)!', r'factorial(\1)', s)

        # Scientific notation 3e8 or 3E8
        s = re.sub(r'(\d+)×10\^([+-]?\d+)', r'(\1*10**\2)', s)
        return s

    def _build_context(self, force_rad: bool = False) -> Dict[str, Any]:
        """Build dictionary of symbols and functions aware of active angle mode."""
        d: Dict[str, Any] = {
            "pi": sp.pi,
            "e": sp.E,
            "ans": self.ans_value,
            "sqrt": sp.sqrt,
            "cbrt": sp.cbrt,
            "abs": sp.Abs,
            "ln": sp.log,
            "log": lambda x, base=10: sp.log(x, base),
            "log10": lambda x: sp.log(x, 10),
            "factorial": sp.factorial,
            "binomial": sp.binomial,
            "gcd": sp.gcd,
            "lcm": sp.lcm,
            "i": sp.I,
        }

        # Add physical constants
        for cname, (cval, _) in self.CONSTANTS.items():
            d[cname] = cval

        # Angle conversions for trigonometric functions
        mode = "RAD" if force_rad else self.angle_mode
        if mode == "DEG":
            d["sin"] = lambda x: sp.sin(x * sp.pi / 180)
            d["cos"] = lambda x: sp.cos(x * sp.pi / 180)
            d["tan"] = lambda x: sp.tan(x * sp.pi / 180)
            d["asin"] = lambda x: sp.asin(x) * 180 / sp.pi
            d["acos"] = lambda x: sp.acos(x) * 180 / sp.pi
            d["atan"] = lambda x: sp.atan(x) * 180 / sp.pi
        elif mode == "GRA":
            d["sin"] = lambda x: sp.sin(x * sp.pi / 200)
            d["cos"] = lambda x: sp.cos(x * sp.pi / 200)
            d["tan"] = lambda x: sp.tan(x * sp.pi / 200)
            d["asin"] = lambda x: sp.asin(x) * 200 / sp.pi
            d["acos"] = lambda x: sp.acos(x) * 200 / sp.pi
            d["atan"] = lambda x: sp.atan(x) * 200 / sp.pi
        else:  # RAD
            d["sin"] = sp.sin
            d["cos"] = sp.cos
            d["tan"] = sp.tan
            d["asin"] = sp.asin
            d["acos"] = sp.acos
            d["atan"] = sp.atan

        # Hyperbolic functions
        d["sinh"] = sp.sinh
        d["cosh"] = sp.cosh
        d["tanh"] = sp.tanh
        d["asinh"] = sp.asinh
        d["acosh"] = sp.acosh
        d["atanh"] = sp.atanh

        return d

    def _format_exact(self, expr: sp.Expr) -> str:
        """Format exact SymPy expression cleanly into textbook style."""
        if expr.is_Rational and not expr.is_Integer:
            return f"{expr.p}/{expr.q}"

        s = sp.pretty(expr, use_unicode=True)
        # If single line, return it directly
        if "\n" not in s:
            return s
        # Otherwise, fall back to simplified string
        return str(expr).replace("**", "^").replace("*", "·")
