"""Interactive Desmos-style Graph Canvas powered by pyqtgraph."""
import re
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont


class DesmosGraphCanvas(QWidget):
    """Interactive 2D Cartesian graphing widget with pan/zoom and cursor tracking."""

    # Signal emitted when mouse moves over the canvas: (x, y)
    mouse_moved = pyqtSignal(float, float)

    # Distinct vibrant curve colors matching dark mode
    PALETTE = [
        "#00d2ff",  # Neon Cyan
        "#ff007f",  # Neon Pink / Magenta
        "#39ff14",  # Neon Lime
        "#ffea00",  # Bright Yellow
        "#bb9af7",  # Soft Violet
        "#ff9e64",  # Neon Orange
        "#2ac3de",  # Sky Blue
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configure pyqtgraph styling
        pg.setConfigOptions(antialias=True, background="#16161e", foreground="#c0caf5")

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # Configure PlotItem
        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.plot_item.setLabel('bottom', "x", **{'font-family': 'monospace', 'font-size': '12pt'})
        self.plot_item.setLabel('left', "y", **{'font-family': 'monospace', 'font-size': '12pt'})

        # Default range [-10, 10]
        self.reset_view()

        # Origin reference lines
        self.h_origin = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen(color="#414868", width=1.5))
        self.v_origin = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen(color="#414868", width=1.5))
        self.plot_item.addItem(self.h_origin)
        self.plot_item.addItem(self.v_origin)

        # Crosshair cursor lines
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color="#565f89", style=Qt.PenStyle.DashLine))
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color="#565f89", style=Qt.PenStyle.DashLine))
        self.plot_item.addItem(self.crosshair_v, ignoreBounds=True)
        self.plot_item.addItem(self.crosshair_h, ignoreBounds=True)

        # Curve items mapping: id -> PlotDataItem
        self.curve_items: dict[str, pg.PlotDataItem] = {}
        # Markers for roots / extrema
        self.marker_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 200))
        self.plot_item.addItem(self.marker_scatter)

        # Connect mouse move event
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_moved)
        self.plot_item.sigRangeChanged.connect(self._on_range_changed)

        self.current_x_range = (-10.0, 10.0)

    def reset_view(self):
        """Reset view to standard [-10, 10] x [-10, 10]."""
        self.plot_item.setXRange(-10, 10, padding=0)
        self.plot_item.setYRange(-10, 10, padding=0)

    def plot_function(self, func_id: str, expr_str: str, color_hex: str, params: dict[str, float] = None):
        """Evaluate and plot a mathematical function f(x)."""
        if not expr_str or not expr_str.strip():
            self.remove_function(func_id)
            return

        x_min, x_max = self.current_x_range
        # Generate dense points for crisp curves (2000 points)
        num_points = 2000
        x_vals = np.linspace(x_min, x_max, num_points)

        try:
            y_vals = self._evaluate_vectorized(expr_str, x_vals, params or {})
            if y_vals is None:
                return

            # Clean discontinuities (e.g. tan(x), 1/x)
            # Mask out non-finite or huge numbers
            diffs = np.abs(np.diff(y_vals))
            threshold = 100 * (abs(np.nanmedian(diffs)) + 1.0)
            discontinuities = np.where(diffs > threshold)[0]
            for idx in discontinuities:
                y_vals[idx] = np.nan

            pen = pg.mkPen(color=color_hex, width=2.5)

            if func_id in self.curve_items:
                self.curve_items[func_id].setData(x_vals, y_vals, pen=pen)
            else:
                curve = self.plot_item.plot(x_vals, y_vals, pen=pen, name=expr_str)
                self.curve_items[func_id] = curve

        except Exception:
            pass

    def remove_function(self, func_id: str):
        """Remove a plotted curve from canvas."""
        if func_id in self.curve_items:
            self.plot_item.removeItem(self.curve_items[func_id])
            del self.curve_items[func_id]

    def clear_all(self):
        """Remove all function curves."""
        for curve in list(self.curve_items.values()):
            self.plot_item.removeItem(curve)
        self.curve_items.clear()
        self.marker_scatter.clear()

    def set_markers(self, points: list[tuple[float, float]], color: str = "#ff9e64"):
        """Plot scatter points (e.g. roots or extrema) on the canvas."""
        self.marker_scatter.clear()
        if not points:
            return
        spots = [{'pos': pt, 'data': 1, 'brush': pg.mkBrush(color)} for pt in points]
        self.marker_scatter.addPoints(spots)

    def _evaluate_vectorized(self, expr_str: str, x: np.ndarray, params: dict[str, float]) -> np.ndarray:
        """Evaluate mathematical function with NumPy vectorization."""
        # Preprocess formula syntax: e.g. ^ -> **, 2x -> 2*x, sin -> np.sin
        s = expr_str.strip()
        s = s.replace("^", "**").replace("×", "*").replace("÷", "/")

        # Replace implicit multiplication like 2x or 3(x)
        s = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', s)
        s = re.sub(r'(\))(x|[a-zA-Z\(])', r'\1*\2', s)

        # Math functions mapping
        safe_env = {
            "x": x,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "asin": np.arcsin,
            "acos": np.arccos,
            "atan": np.arctan,
            "sinh": np.sinh,
            "cosh": np.cosh,
            "tanh": np.tanh,
            "sqrt": np.sqrt,
            "cbrt": np.cbrt,
            "exp": np.exp,
            "ln": np.log,
            "log": np.log10,
            "log2": np.log2,
            "abs": np.abs,
            "pi": np.pi,
            "e": np.e,
        }

        # Add parameters (sliders)
        for k, v in params.items():
            safe_env[k] = v

        try:
            with np.errstate(all='ignore'):
                y = eval(s, {"__builtins__": {}}, safe_env)
                if isinstance(y, (int, float)):
                    y = np.full_like(x, float(y))
                return y
        except Exception:
            return None

    def _on_mouse_moved(self, pos):
        """Track mouse coordinates and update crosshairs."""
        if self.plot_item.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_item.vb.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            self.crosshair_v.setPos(x)
            self.crosshair_h.setPos(y)
            self.mouse_moved.emit(x, y)

    def _on_range_changed(self, view, ranges):
        """Update x range bounds when user pans or zooms."""
        self.current_x_range = ranges[0]
