"""Desmos-style Graphing Panel with multi-function input, sliders, and analysis."""
import uuid
from typing import Dict, Any, Callable
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QLineEdit,
    QLabel,
    QScrollArea,
    QFrame,
    QSlider,
    QCheckBox,
    QMenu,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction

from src.desmos.graph_canvas import DesmosGraphCanvas
from src.desmos.analysis import CurveAnalyzer


class FunctionRow(QFrame):
    """Row widget for managing a single function formula, color, and visibility."""

    changed = pyqtSignal(str)   # emits func_id
    deleted = pyqtSignal(str)   # emits func_id

    def __init__(self, func_id: str, default_expr: str, color_hex: str, parent=None):
        super().__init__(parent)
        self.func_id = func_id
        self.color_hex = color_hex

        self.setObjectName("FunctionRow")
        self.setStyleSheet("""
            QFrame#FunctionRow {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 6px;
                margin-bottom: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Color tag
        self.color_badge = QPushButton()
        self.color_badge.setFixedSize(16, 16)
        self.color_badge.setStyleSheet(f"background-color: {self.color_hex}; border: none; border-radius: 8px;")
        layout.addWidget(self.color_badge)

        # Formula label: f(x) =
        lbl = QLabel("f(x) =")
        lbl.setStyleSheet("color: #cdd6f4; font-family: monospace; font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        # Input line edit
        self.input_edit = QLineEdit(default_expr)
        self.input_edit.setStyleSheet("""
            QLineEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
        """)
        self.input_edit.textChanged.connect(lambda: self.changed.emit(self.func_id))
        layout.addWidget(self.input_edit)

        # Visible checkbox
        self.vis_checkbox = QCheckBox()
        self.vis_checkbox.setChecked(True)
        self.vis_checkbox.setToolTip("Toggle curve visibility")
        self.vis_checkbox.stateChanged.connect(lambda: self.changed.emit(self.func_id))
        layout.addWidget(self.vis_checkbox)

        # Delete button
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f38ba8;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #313244;
                border-radius: 12px;
            }
        """)
        del_btn.clicked.connect(lambda: self.deleted.emit(self.func_id))
        layout.addWidget(del_btn)

    @property
    def expression(self) -> str:
        return self.input_edit.text().strip()

    @property
    def is_visible(self) -> bool:
        return self.vis_checkbox.isChecked()


class DesmosWidget(QWidget):
    """Complete Desmos graphing environment with function manager and analysis."""

    request_manim_export = pyqtSignal(list)  # Emits list of active (expr_str, color)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.functions: dict[str, FunctionRow] = {}
        self.slider_params: dict[str, float] = {"a": 1.0, "b": 1.0}

        self._init_ui()

        # Add initial starter functions
        self.add_function("sin(x)")
        self.add_function("0.2 * x^2 - 3")

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #313244;
                width: 4px;
            }
        """)

        # Left Panel: Expression list and tools
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(8)

        # Title bar & Actions
        header_layout = QHBoxLayout()
        title = QLabel("FUNCTIONS")
        title.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 13px; font-family: monospace;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        presets_btn = QPushButton("📚 Common Functions")
        presets_btn.setToolTip("Browse and insert standard mathematical functions")
        presets_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #f9e2af;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45475a;
                color: #ffffff;
            }
        """)
        presets_btn.clicked.connect(lambda: self._open_presets_menu(presets_btn))
        header_layout.addWidget(presets_btn)

        add_btn = QPushButton("+ Add")
        add_btn.setToolTip("Add new expression row")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_function(""))
        header_layout.addWidget(add_btn)
        left_layout.addLayout(header_layout)

        # Scroll area for functions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.func_container = QWidget()
        self.func_list_layout = QVBoxLayout(self.func_container)
        self.func_list_layout.setContentsMargins(0, 0, 0, 0)
        self.func_list_layout.setSpacing(4)
        self.func_list_layout.addStretch()
        scroll_area.setWidget(self.func_container)
        left_layout.addWidget(scroll_area, stretch=3)

        # Parameter Sliders Section (a and b)
        slider_frame = QFrame()
        slider_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 6px;")
        slider_layout = QVBoxLayout(slider_frame)
        slider_layout.setContentsMargins(8, 6, 8, 6)

        sl_title = QLabel("DYNAMIC PARAMETER SLIDERS")
        sl_title.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; font-family: monospace;")
        slider_layout.addWidget(sl_title)

        # Slider a
        a_row = QHBoxLayout()
        self.a_label = QLabel("a = 1.0")
        self.a_label.setStyleSheet("color: #00d2ff; font-weight: bold; font-family: monospace;")
        self.slider_a = QSlider(Qt.Orientation.Horizontal)
        self.slider_a.setRange(-50, 50)
        self.slider_a.setValue(10)
        self.slider_a.valueChanged.connect(self._on_slider_changed)
        a_row.addWidget(self.a_label)
        a_row.addWidget(self.slider_a)
        slider_layout.addLayout(a_row)

        # Slider b
        b_row = QHBoxLayout()
        self.b_label = QLabel("b = 1.0")
        self.b_label.setStyleSheet("color: #ff007f; font-weight: bold; font-family: monospace;")
        self.slider_b = QSlider(Qt.Orientation.Horizontal)
        self.slider_b.setRange(1, 50)
        self.slider_b.setValue(10)
        self.slider_b.valueChanged.connect(self._on_slider_changed)
        b_row.addWidget(self.b_label)
        b_row.addWidget(self.slider_b)
        slider_layout.addLayout(b_row)

        left_layout.addWidget(slider_frame)

        # Curve Analysis Tools
        tools_frame = QFrame()
        tools_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 6px;")
        tools_layout = QVBoxLayout(tools_frame)
        tools_layout.setContentsMargins(8, 6, 8, 6)

        tool_title = QLabel("CURVE ANALYSIS")
        tool_title.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; font-family: monospace;")
        tools_layout.addWidget(tool_title)

        btn_row = QHBoxLayout()
        root_btn = QPushButton("Find Roots (0)")
        root_btn.setStyleSheet("background-color: #313244; color: #a6e3a1; font-weight: 600; padding: 6px; border-radius: 6px;")
        root_btn.clicked.connect(self.analyze_roots)
        btn_row.addWidget(root_btn)

        extrema_btn = QPushButton("Extrema (Min/Max)")
        extrema_btn.setStyleSheet("background-color: #313244; color: #f9e2af; font-weight: 600; padding: 6px; border-radius: 6px;")
        extrema_btn.clicked.connect(self.analyze_extrema)
        btn_row.addWidget(extrema_btn)
        tools_layout.addLayout(btn_row)

        self.analysis_label = QLabel("Hover over curves or analyze roots/extrema.")
        self.analysis_label.setStyleSheet("color: #cdd6f4; font-size: 11px; font-family: monospace;")
        self.analysis_label.setWordWrap(True)
        tools_layout.addWidget(self.analysis_label)

        left_layout.addWidget(tools_frame)

        # Right Panel: Canvas & Controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Top Control Bar
        top_bar = QHBoxLayout()
        self.coord_label = QLabel("X: 0.00   Y: 0.00")
        self.coord_label.setStyleSheet("color: #89b4fa; font-family: monospace; font-size: 13px; font-weight: bold;")
        top_bar.addWidget(self.coord_label)

        top_bar.addStretch()

        reset_btn = QPushButton("⟲ Reset View")
        reset_btn.setStyleSheet("background-color: #313244; color: #cdd6f4; border-radius: 6px; padding: 4px 10px;")
        reset_btn.clicked.connect(self.canvas_reset)
        top_bar.addWidget(reset_btn)

        manim_btn = QPushButton("🎬 Animate in Manim")
        manim_btn.setStyleSheet("""
            QPushButton {
                background-color: #fab387;
                color: #11111b;
                font-weight: bold;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #f9e2af;
            }
        """)
        manim_btn.clicked.connect(self._trigger_manim_export)
        top_bar.addWidget(manim_btn)

        right_layout.addLayout(top_bar)

        # Canvas
        self.canvas = DesmosGraphCanvas(self)
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        right_layout.addWidget(self.canvas)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

    def add_function(self, expr: str = ""):
        """Add new function row to the list."""
        func_id = str(uuid.uuid4())
        palette_idx = len(self.functions) % len(DesmosGraphCanvas.PALETTE)
        color = DesmosGraphCanvas.PALETTE[palette_idx]

        row = FunctionRow(func_id, expr, color, self.func_container)
        row.changed.connect(self.update_single_function)
        row.deleted.connect(self.delete_function)

        self.functions[func_id] = row
        # Insert before stretch
        self.func_list_layout.insertWidget(self.func_list_layout.count() - 1, row)

        if expr:
            self.update_single_function(func_id)

    def update_single_function(self, func_id: str):
        """Re-render a specific function."""
        if func_id not in self.functions:
            return

        row = self.functions[func_id]
        if not row.is_visible or not row.expression:
            self.canvas.remove_function(func_id)
        else:
            self.canvas.plot_function(func_id, row.expression, row.color_hex, self.slider_params)

    def update_all_functions(self):
        """Re-render all active functions."""
        for fid in list(self.functions.keys()):
            self.update_single_function(fid)

    def delete_function(self, func_id: str):
        """Remove a function row and its curve."""
        if func_id in self.functions:
            row = self.functions.pop(func_id)
            self.func_list_layout.removeWidget(row)
            row.deleteLater()
            self.canvas.remove_function(func_id)

    def _on_slider_changed(self):
        """Handle dynamic parameter slider changes."""
        val_a = self.slider_a.value() / 10.0
        val_b = self.slider_b.value() / 10.0
        self.slider_params["a"] = val_a
        self.slider_params["b"] = val_b
        self.a_label.setText(f"a = {val_a:.1f}")
        self.b_label.setText(f"b = {val_b:.1f}")
        self.update_all_functions()

    def _on_mouse_moved(self, x: float, y: float):
        """Display tracked coordinates in real-time."""
        self.coord_label.setText(f"X: {x:8.3f}   Y: {y:8.3f}")

    def canvas_reset(self):
        self.canvas.reset_view()

    def analyze_roots(self):
        """Analyze and display roots of the first visible curve."""
        active_row = next((r for r in self.functions.values() if r.is_visible and r.expression), None)
        if not active_row:
            self.analysis_label.setText("No active function to analyze.")
            return

        expr = active_row.expression
        eval_fn = lambda x: float(self.canvas._evaluate_vectorized(expr, np.array([x]), self.slider_params)[0])
        xmin, xmax = self.canvas.current_x_range
        roots = CurveAnalyzer.find_roots(eval_fn, xmin, xmax)

        if roots:
            pts = [(r, 0.0) for r in roots]
            self.canvas.set_markers(pts, color="#a6e3a1")
            self.analysis_label.setText(f"Roots ({active_row.expression}): {', '.join(str(r) for r in roots[:6])}")
        else:
            self.canvas.set_markers([])
            self.analysis_label.setText(f"No real roots found for {active_row.expression} in [{xmin:.1f}, {xmax:.1f}].")

    def analyze_extrema(self):
        """Analyze and display local minima/maxima."""
        active_row = next((r for r in self.functions.values() if r.is_visible and r.expression), None)
        if not active_row:
            self.analysis_label.setText("No active function to analyze.")
            return

        expr = active_row.expression
        eval_fn = lambda x: float(self.canvas._evaluate_vectorized(expr, np.array([x]), self.slider_params)[0])
        xmin, xmax = self.canvas.current_x_range
        extrema = CurveAnalyzer.find_extrema(eval_fn, xmin, xmax)

        if extrema:
            pts = [(x, y) for x, y, _ in extrema]
            self.canvas.set_markers(pts, color="#f9e2af")
            desc = [f"{t.upper()}: ({x}, {y})" for x, y, t in extrema[:4]]
            self.analysis_label.setText(" | ".join(desc))
        else:
            self.canvas.set_markers([])
            self.analysis_label.setText(f"No extrema found for {active_row.expression} in [{xmin:.1f}, {xmax:.1f}].")

    def _trigger_manim_export(self):
        """Collect visible mathematical expressions and trigger Manim Studio."""
        items = [(r.expression, r.color_hex) for r in self.functions.values() if r.is_visible and r.expression]
        if not items:
            QMessageBox.information(self, "No Functions", "Please add at least one visible function curve to animate in Manim.")
            return
        self.request_manim_export.emit(items)

    def _open_presets_menu(self, btn: QPushButton):
        """Display categorized library of standard mathematical functions."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 4px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
                color: #89b4fa;
            }
        """)

        categories = {
            "📐 Trigonometric & Waves": [
                ("Sine Wave", "sin(x)"),
                ("Cosine Wave", "cos(x)"),
                ("Tangent (with asymptotes)", "tan(x)"),
                ("Sinc Function [sin(x)/x]", "sin(x) / x"),
                ("Damped Harmonic Oscillator", "exp(-0.2*x) * cos(3*x)"),
                ("Wave Interference / Beats", "sin(4*x) + sin(4.4*x)"),
                ("Fourier Square Wave Approximation", "sin(x) + sin(3*x)/3 + sin(5*x)/5"),
                ("Topologist's Sine Curve", "sin(1/x)"),
            ],
            "📈 Polynomials & Rational": [
                ("Parabola", "x^2 - 4"),
                ("Cubic Polynomial", "x^3 - 3*x"),
                ("Double-Well Potential", "x^4 - 4*x^2 + 1"),
                ("Rational Hyperbola", "1 / x"),
                ("Runge's Phenomenon", "1 / (1 + 25*x^2)"),
                ("Cube Root Curve", "cbrt(x)"),
            ],
            "⚡ Exponential & Logarithmic": [
                ("Natural Exponential (eˣ)", "exp(x)"),
                ("Natural Logarithm (ln x)", "ln(x)"),
                ("Logistic / Sigmoid Activation", "1 / (1 + exp(-x))"),
                ("Gaussian Normal Distribution", "exp(-x^2 / 2) / sqrt(2*pi)"),
            ],
            "✨ Special & Parametric Curves": [
                ("Absolute Value V-Shape", "abs(x)"),
                ("Bouncing Wave |sin(x)|", "abs(sin(x))"),
                ("Semicircle (Radius 5)", "sqrt(abs(25 - x^2))"),
                ("Dynamic Parametric Wave", "a * sin(b * x)"),
            ],
        }

        for cat_name, funcs in categories.items():
            sub = menu.addMenu(cat_name)
            sub.setStyleSheet(menu.styleSheet())
            for label, expr in funcs:
                act = QAction(f"{label}  [{expr}]", self)
                act.triggered.connect(lambda _, e=expr: self.add_function(e))
                sub.addAction(act)

        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

