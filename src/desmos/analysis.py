"""Numerical analysis tools for graphing curves: roots, extrema, integrals."""
import numpy as np
import scipy.optimize as opt
from typing import List, Tuple, Callable


class CurveAnalyzer:
    """Calculates roots, extrema, and numerical integrals for plotted functions."""

    @staticmethod
    def find_roots(func: Callable[[float], float], x_min: float, x_max: float, samples: int = 400) -> List[float]:
        """Find real roots f(x) = 0 in [x_min, x_max]."""
        roots = []
        xs = np.linspace(x_min, x_max, samples)
        ys = []
        valid_xs = []

        for x in xs:
            try:
                y = func(x)
                if np.isfinite(y):
                    ys.append(y)
                    valid_xs.append(x)
            except Exception:
                pass

        if len(ys) < 2:
            return roots

        # Look for sign changes
        for i in range(len(ys) - 1):
            if ys[i] == 0:
                roots.append(round(valid_xs[i], 6))
            elif ys[i] * ys[i+1] < 0:
                try:
                    sol = opt.brentq(func, valid_xs[i], valid_xs[i+1])
                    if np.isfinite(sol):
                        r = round(float(sol), 6)
                        if not any(abs(r - existing) < 1e-4 for existing in roots):
                            roots.append(r)
                except Exception:
                    pass

        return sorted(roots)

    @staticmethod
    def find_extrema(func: Callable[[float], float], x_min: float, x_max: float, samples: int = 300) -> List[Tuple[float, float, str]]:
        """Find local minima and maxima (x, y, 'min'|'max') in [x_min, x_max]."""
        extrema = []
        xs = np.linspace(x_min, x_max, samples)
        vals = []

        for x in xs:
            try:
                y = func(x)
                if np.isfinite(y):
                    vals.append((x, y))
            except Exception:
                pass

        if len(vals) < 3:
            return extrema

        for i in range(1, len(vals) - 1):
            prev_y = vals[i-1][1]
            curr_x, curr_y = vals[i]
            next_y = vals[i+1][1]

            low_b = vals[max(0, i - 2)][0]
            high_b = vals[min(len(vals) - 1, i + 2)][0]

            # Local maximum (including plateau detection)
            if curr_y >= prev_y and curr_y >= next_y and (curr_y > prev_y or curr_y > next_y):
                try:
                    res = opt.minimize_scalar(lambda x: -func(x), bounds=(low_b, high_b), method='bounded')
                    if res.success:
                        pt = (round(float(res.x), 6), round(float(-res.fun), 6), "max")
                        if not any(abs(pt[0] - ex[0]) < 1e-3 for ex in extrema):
                            extrema.append(pt)
                except Exception:
                    pt = (round(curr_x, 6), round(curr_y, 6), "max")
                    if not any(abs(pt[0] - ex[0]) < 1e-3 for ex in extrema):
                        extrema.append(pt)

            # Local minimum
            elif curr_y <= prev_y and curr_y <= next_y and (curr_y < prev_y or curr_y < next_y):
                try:
                    res = opt.minimize_scalar(func, bounds=(low_b, high_b), method='bounded')
                    if res.success:
                        pt = (round(float(res.x), 6), round(float(res.fun), 6), "min")
                        if not any(abs(pt[0] - ex[0]) < 1e-3 for ex in extrema):
                            extrema.append(pt)
                except Exception:
                    pt = (round(curr_x, 6), round(curr_y, 6), "min")
                    if not any(abs(pt[0] - ex[0]) < 1e-3 for ex in extrema):
                        extrema.append(pt)

        return extrema

    @staticmethod
    def integrate_area(func: Callable[[float], float], a: float, b: float, n_points: int = 1000) -> float:
        """Compute numerical integral ∫_a^b f(x) dx via Simpson's rule."""
        xs = np.linspace(a, b, n_points)
        ys = []
        for x in xs:
            try:
                val = func(x)
                ys.append(val if np.isfinite(val) else 0.0)
            except Exception:
                ys.append(0.0)

        # Trapezoidal numerical integration
        return float(np.trapezoid(ys, xs))
