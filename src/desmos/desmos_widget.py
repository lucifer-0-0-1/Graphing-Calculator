"""Desmos-style Interactive Graphing Panel with multi-function input, dynamic parameter sliders, and analysis."""
import uuid
import numpy as np
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
    QDoubleSpinBox,
    QDialog,
    QFormLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction, QKeySequence, QShortcut

from src.desmos.graph_canvas import DesmosGraphCanvas
from src.desmos.analysis import CurveAnalyzer


class AddParameterDialog(QDialog):
    """Dialog to create a new dynamic mathematical parameter slider."""

    def __init__(self, existing_params: set[str], parent=None):
        super().__init__(parent)
        self.existing_params = existing_params
        self.setWindowTitle("Add Dynamic Parameter Slider")
        self.setMinimumWidth(320)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-family: monospace;
                font-size: 12px;
            }
            QLineEdit, QDoubleSpinBox {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
                font-family: monospace;
            }
            QLineEdit:focus, QDoubleSpinBox:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("CREATE DYNAMIC PARAMETER")
        header.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 13px;")
        layout.addWidget(header)

        form = QFormLayout()

        # Suggest next unused letter
        candidates = ["c", "d", "k", "m", "n", "w", "p", "q", "v", "t", "r", "s", "z"]
        suggested = next((ch for ch in candidates if ch not in self.existing_params), "k")

        self.name_edit = QLineEdit(suggested)
        self.name_edit.setPlaceholderText("Parameter variable name (e.g. c, k, m)")
        form.addRow("Variable Name:", self.name_edit)

        self.val_spin = QDoubleSpinBox()
        self.val_spin.setRange(-1000.0, 1000.0)
        self.val_spin.setValue(1.0)
        self.val_spin.setDecimals(2)
        form.addRow("Initial Value:", self.val_spin)

        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(-10000.0, 10000.0)
        self.min_spin.setValue(-10.0)
        self.min_spin.setDecimals(1)
        form.addRow("Minimum Bound:", self.min_spin)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(-10000.0, 10000.0)
        self.max_spin.setValue(10.0)
        self.max_spin.setDecimals(1)
        form.addRow("Maximum Bound:", self.max_spin)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #313244; color: #cdd6f4;")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        add_btn = QPushButton("Create Slider")
        add_btn.clicked.connect(self._validate_and_accept)
        btn_row.addWidget(add_btn)

        layout.addLayout(btn_row)

    def _validate_and_accept(self):
        name = self.name_edit.text().strip()
        reserved = {
            "x", "y", "sin", "cos", "tan", "asin", "acos", "atan",
            "sinh", "cosh", "tanh", "sqrt", "cbrt", "exp", "ln",
            "log", "log2", "abs", "floor", "ceil", "pi", "e"
        }
        if not name or not name.isidentifier():
            QMessageBox.warning(self, "Invalid Name", "Parameter name must be a valid identifier (e.g., c, k, m, omega).")
            return
        if name in reserved:
            QMessageBox.warning(self, "Reserved Name", f"'{name}' is a reserved function or variable in the engine.")
            return
        if name in self.existing_params:
            QMessageBox.warning(self, "Duplicate Parameter", f"Parameter '{name}' already exists.")
            return
        if self.min_spin.value() >= self.max_spin.value():
            QMessageBox.warning(self, "Invalid Bounds", "Minimum bound must be strictly less than maximum bound.")
            return

        self.accept()

    def get_data(self) -> tuple[str, float, float, float]:
        return (
            self.name_edit.text().strip(),
            self.val_spin.value(),
            self.min_spin.value(),
            self.max_spin.value(),
        )


class ParameterSliderRow(QFrame):
    """Interactive slider widget for a single dynamic mathematical parameter."""

    value_changed = pyqtSignal(str, float)  # param_name, new_val
    deleted = pyqtSignal(str)               # param_name

    def __init__(self, name: str, value: float, min_val: float, max_val: float, color_hex: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.color_hex = color_hex
        self.ticks = 200

        self.setObjectName("ParamRow")
        self.setStyleSheet("""
            QFrame#ParamRow {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 4px;
                margin-bottom: 2px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # Name label
        lbl = QLabel(f"<b>{name}</b> =")
        lbl.setStyleSheet(f"color: {color_hex}; font-family: monospace; font-size: 13px; font-weight: bold; min-width: 32px;")
        layout.addWidget(lbl)

        # Double spinbox for exact numerical value
        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setDecimals(2)
        self.spin.setSingleStep(0.1)
        self.spin.setValue(value)
        self.spin.setFixedWidth(72)
        self.spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #11111b;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 2px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.spin)

        # Horizontal slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.ticks)
        self._set_slider_from_val(value)
        layout.addWidget(self.slider)

        # Delete button
        del_btn = QPushButton("✕")
        del_btn.setToolTip(f"Remove parameter '{name}'")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f38ba8;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #313244;
                border-radius: 10px;
            }
        """)
        del_btn.clicked.connect(lambda: self.deleted.emit(self.name))
        layout.addWidget(del_btn)

        # Synchronization
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spin.valueChanged.connect(self._on_spin_changed)

    def _val_to_tick(self, val: float) -> int:
        if self.max_val == self.min_val:
            return 0
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        ratio = max(0.0, min(1.0, ratio))
        return int(round(ratio * self.ticks))

    def _tick_to_val(self, tick: int) -> float:
        ratio = tick / float(self.ticks)
        return self.min_val + ratio * (self.max_val - self.min_val)

    def _set_slider_from_val(self, val: float):
        self.slider.blockSignals(True)
        self.slider.setValue(self._val_to_tick(val))
        self.slider.blockSignals(False)

    def _on_slider_changed(self, tick: int):
        val = round(self._tick_to_val(tick), 2)
        self.spin.blockSignals(True)
        self.spin.setValue(val)
        self.spin.blockSignals(False)
        self.value_changed.emit(self.name, val)

    def _on_spin_changed(self, val: float):
        self._set_slider_from_val(val)
        self.value_changed.emit(self.name, val)

    @property
    def value(self) -> float:
        return self.spin.value()


class FunctionRow(QFrame):
    """Row widget for managing a single function formula, color, and visibility."""

    changed = pyqtSignal(str)   # emits func_id
    deleted = pyqtSignal(str)   # emits func_id
    enter_pressed = pyqtSignal(str)  # emits func_id on Enter/Return

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
        self.input_edit.returnPressed.connect(lambda: self.enter_pressed.emit(self.func_id))
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
    """Complete Desmos graphing environment with function manager, dynamic sliders, and analysis."""

    PARAM_PALETTE = [
        "#00d2ff",  # Neon Cyan
        "#ff007f",  # Neon Pink
        "#39ff14",  # Neon Lime
        "#ffea00",  # Bright Yellow
        "#bb9af7",  # Soft Violet
        "#ff9e64",  # Neon Orange
        "#2ac3de",  # Sky Blue
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.functions: dict[str, FunctionRow] = {}
        self.slider_params: dict[str, float] = {}
        self.param_rows: dict[str, ParameterSliderRow] = {}

        self._init_ui()

        # Add initial dynamic parameter sliders (a and b)
        self.add_parameter("a", 1.0, -10.0, 10.0)
        self.add_parameter("b", 1.0, 0.1, 10.0)

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

        # Left Panel: Expression list, dynamic sliders, and analysis
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
        add_btn.setToolTip("Add new expression row (Shortcut: Ctrl+N)")
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

        # Dynamic Parameter Sliders Section
        slider_frame = QFrame()
        slider_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 8px; padding: 6px;")
        slider_layout = QVBoxLayout(slider_frame)
        slider_layout.setContentsMargins(8, 6, 8, 6)
        slider_layout.setSpacing(6)

        sl_header = QHBoxLayout()
        sl_title = QLabel("DYNAMIC PARAMETER SLIDERS")
        sl_title.setStyleSheet("color: #a6adc8; font-size: 11px; font-weight: bold; font-family: monospace;")
        sl_header.addWidget(sl_title)

        sl_header.addStretch()

        add_param_btn = QPushButton("+ Add Slider")
        add_param_btn.setToolTip("Create a new dynamic mathematical parameter (Shortcut: Ctrl+P)")
        add_param_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        add_param_btn.clicked.connect(self._prompt_add_parameter)
        sl_header.addWidget(add_param_btn)
        slider_layout.addLayout(sl_header)

        # Container for parameter slider rows
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(4)
        slider_layout.addWidget(self.params_container)

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
        reset_btn.setToolTip("Reset canvas zoom and pan to [-10, 10] (Shortcut: Ctrl+R)")
        reset_btn.setStyleSheet("background-color: #313244; color: #cdd6f4; border-radius: 6px; padding: 4px 10px;")
        reset_btn.clicked.connect(self.canvas_reset)
        top_bar.addWidget(reset_btn)

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

        # Desmos Keyboard Navigation Shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(lambda: self.add_function(""))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.canvas_reset)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self._prompt_add_parameter)

    def focus_first_input(self):
        """Focus the first expression row input."""
        if self.functions:
            first_row = next(iter(self.functions.values()))
            first_row.input_edit.setFocus()
            first_row.input_edit.selectAll()

    def _on_row_enter_pressed(self, func_id: str):
        """When user presses Enter in a function row, focus next or create new row."""
        row_ids = list(self.functions.keys())
        if func_id in row_ids:
            idx = row_ids.index(func_id)
            if idx == len(row_ids) - 1:
                self.add_function("")
                if self.functions:
                    last_row = list(self.functions.values())[-1]
                    last_row.input_edit.setFocus()
            else:
                next_id = row_ids[idx + 1]
                self.functions[next_id].input_edit.setFocus()
                self.functions[next_id].input_edit.selectAll()

    def add_function(self, expr: str = ""):
        """Add new function row to the list."""
        func_id = str(uuid.uuid4())
        palette_idx = len(self.functions) % len(DesmosGraphCanvas.PALETTE)
        color = DesmosGraphCanvas.PALETTE[palette_idx]

        row = FunctionRow(func_id, expr, color, self.func_container)
        row.changed.connect(self.update_single_function)
        row.deleted.connect(self.delete_function)
        row.enter_pressed.connect(self._on_row_enter_pressed)

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

    # -------------------------------------------------------------
    # Dynamic Parameter Slider Management
    # -------------------------------------------------------------
    def add_parameter(self, name: str, value: float = 1.0, min_val: float = -10.0, max_val: float = 10.0):
        """Add a dynamic parameter slider to the UI and canvas environment."""
        if name in self.param_rows:
            return

        color_idx = len(self.param_rows) % len(self.PARAM_PALETTE)
        color = self.PARAM_PALETTE[color_idx]

        row = ParameterSliderRow(name, value, min_val, max_val, color, self.params_container)
        row.value_changed.connect(self._on_param_changed)
        row.deleted.connect(self.remove_parameter)

        self.param_rows[name] = row
        self.slider_params[name] = value
        self.params_layout.addWidget(row)
        self.update_all_functions()

    def remove_parameter(self, name: str):
        """Remove a dynamic parameter slider."""
        if name in self.param_rows:
            row = self.param_rows.pop(name)
            self.params_layout.removeWidget(row)
            row.deleteLater()

        if name in self.slider_params:
            del self.slider_params[name]

        self.update_all_functions()

    def _prompt_add_parameter(self):
        """Display dialog to create a custom dynamic parameter slider."""
        dlg = AddParameterDialog(set(self.slider_params.keys()), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, val, min_v, max_v = dlg.get_data()
            self.add_parameter(name, val, min_v, max_v)

    def _on_param_changed(self, name: str, val: float):
        """Update parameter value and re-evaluate curves dynamically."""
        self.slider_params[name] = val
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
