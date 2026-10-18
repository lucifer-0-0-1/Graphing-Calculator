"""Casio Equation & System Solver (Simultaneous & Polynomials)."""
import sympy as sp
from typing import Tuple, List, Dict, Any


class EquationSolver:
    """Solves algebraic polynomials and simultaneous equation systems like Casio fx-991CW."""

    @staticmethod
    def solve_quadratic(a: float, b: float, c: float) -> Dict[str, Any]:
        """Solve ax² + bx + c = 0."""
        if a == 0:
            if b == 0:
                return {"error": "Invalid equation (0 = 0 or c = 0)"}
            return {
                "type": "linear",
                "roots": [-c / b],
                "roots_exact": [f"{-c / b:.6g}"],
                "discriminant": 0,
            }

        x = sp.Symbol('x')
        eq = a * x**2 + b * x + c
        solutions = sp.solve(eq, x)

        discriminant = b**2 - 4 * a * c
        vertex_x = -b / (2 * a)
        vertex_y = c - (b**2) / (4 * a)

        roots_formatted = []
        for s in solutions:
            approx = complex(sp.N(s, 8))
            if abs(approx.imag) < 1e-10:
                roots_formatted.append(f"{approx.real:.8g}")
            else:
                sign = "+" if approx.imag >= 0 else "-"
                roots_formatted.append(f"{approx.real:.8g} {sign} {abs(approx.imag):.8g}i")

        return {
            "type": "quadratic",
            "roots": roots_formatted,
            "roots_exact": [str(s) for s in solutions],
            "discriminant": discriminant,
            "vertex": (vertex_x, vertex_y),
            "nature": "2 Real distinct" if discriminant > 0 else ("1 Repeated real" if discriminant == 0 else "2 Complex conjugate"),
        }

    @staticmethod
    def solve_cubic(a: float, b: float, c: float, d: float) -> Dict[str, Any]:
        """Solve ax³ + bx² + cx + d = 0."""
        if a == 0:
            return EquationSolver.solve_quadratic(b, c, d)

        x = sp.Symbol('x')
        eq = a * x**3 + b * x**2 + c * x + d
        solutions = sp.solve(eq, x)

        roots_formatted = []
        for s in solutions:
            approx = complex(sp.N(s, 8))
            if abs(approx.imag) < 1e-10:
                roots_formatted.append(f"{approx.real:.8g}")
            else:
                sign = "+" if approx.imag >= 0 else "-"
                roots_formatted.append(f"{approx.real:.8g} {sign} {abs(approx.imag):.8g}i")

        return {
            "type": "cubic",
            "roots": roots_formatted,
            "roots_exact": [str(s) for s in solutions],
        }

    @staticmethod
    def solve_linear_2x2(a1: float, b1: float, c1: float,
                          a2: float, b2: float, c2: float) -> Dict[str, Any]:
        """
        Solve 2-variable linear system:
        a1·x + b1·y = c1
        a2·x + b2·y = c2
        """
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-12:
            return {"error": "System has infinite solutions or no solution (det = 0)"}

        x_val = (c1 * b2 - c2 * b1) / det
        y_val = (a1 * c2 - a2 * c1) / det

        return {
            "type": "2x2_system",
            "x": f"{x_val:.8g}",
            "y": f"{y_val:.8g}",
            "determinant": det,
        }

    @staticmethod
    def solve_linear_3x3(rows: List[List[float]]) -> Dict[str, Any]:
        """
        Solve 3-variable linear system given 3 rows: [a, b, c, d] for a·x + b·y + c·z = d.
        """
        try:
            x, y, z = sp.symbols('x y z')
            eqs = [
                sp.Eq(rows[0][0]*x + rows[0][1]*y + rows[0][2]*z, rows[0][3]),
                sp.Eq(rows[1][0]*x + rows[1][1]*y + rows[1][2]*z, rows[1][3]),
                sp.Eq(rows[2][0]*x + rows[2][1]*y + rows[2][2]*z, rows[2][3]),
            ]
            sol = sp.solve(eqs, (x, y, z))
            if not sol:
                return {"error": "No unique solution found"}

            return {
                "type": "3x3_system",
                "x": f"{float(sp.N(sol[x], 8)):.8g}",
                "y": f"{float(sp.N(sol[y], 8)):.8g}",
                "z": f"{float(sp.N(sol[z], 8)):.8g}",
            }
        except Exception as e:
            return {"error": f"Failed to solve: {e}"}
