"""Casio fx-991CW ClassWiz Scientific Calculator UI Widget with Full Keyboard Support."""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSizePolicy,
    QMenu,
    QDialog,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QKeySequence, QShortcut

from src.casio.casio_engine import CasioEngine
from src.casio.equation_solver import EquationSolver


class CasioLineEdit(QLineEdit):
    """Custom interactive QLineEdit for Casio LCD with keyboard-first operation."""

    evaluate_requested = pyqtSignal()
    ac_requested = pyqtSignal()
    sd_requested = pyqtSignal()
    history_prev_requested = pyqtSignal()
    history_next_requested = pyqtSignal()
    angle_toggle_requested = pyqtSignal()
    solver_requested = pyqtSignal()
    constants_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_casio = parent
        self.setPlaceholderText("Type expression (e.g. sin(45) + 2*pi) or click buttons...")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #79c0ff;
                font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace;
                font-size: 20px;
                min-height: 32px;
                selection-background-color: #1f6feb;
                selection-color: #ffffff;
            }
        """)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        # Enter / Return or unshifted '=' evaluates expression
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.evaluate_requested.emit()
            return
        if key == Qt.Key.Key_Equal and not (modifiers & Qt.KeyboardModifier.ShiftModifier):
            self.evaluate_requested.emit()
            return

        # Escape clears (AC)
        if key == Qt.Key.Key_Escape:
            self.ac_requested.emit()
            return

        # Tab or Ctrl+D toggles S <=> D (Exact <-> Decimal)
        if key == Qt.Key.Key_Tab or (key == Qt.Key.Key_D and (modifiers & Qt.KeyboardModifier.ControlModifier)):
            self.sd_requested.emit()
            return

        # Up / Down arrows navigate calculation history
        if key == Qt.Key.Key_Up:
            self.history_prev_requested.emit()
            return
        if key == Qt.Key.Key_Down:
            self.history_next_requested.emit()
            return

        # F2 toggles angle mode (DEG -> RAD -> GRA)
        if key == Qt.Key.Key_F2:
            self.angle_toggle_requested.emit()
            return

        # F3 or Ctrl+E opens Equation Solver
        if key == Qt.Key.Key_F3 or (key == Qt.Key.Key_E and (modifiers & Qt.KeyboardModifier.ControlModifier)):
            self.solver_requested.emit()
            return

        # F4 or Ctrl+P opens Constants Menu
        if key == Qt.Key.Key_F4 or (key == Qt.Key.Key_P and (modifiers & Qt.KeyboardModifier.ControlModifier)):
            self.constants_requested.emit()
            return

        # Copy result to clipboard on Ctrl+C if formula has no selection
        if key == Qt.Key.Key_C and (modifiers & Qt.KeyboardModifier.ControlModifier):
            if not self.hasSelectedText() and self.parent_casio and hasattr(self.parent_casio, "result_label"):
                clipboard = QApplication.clipboard()
                if clipboard:
                    clipboard.setText(self.parent_casio.result_label.text())
                    return

        # Replace typed keyboard operators with clean Casio LCD glyphs
        text = event.text()
        if text == "*":
            self.insert("×")
            return
        elif text == "/":
            self.insert("÷")
            return

        super().keyPressEvent(event)


class EquationSolverDialog(QDialog):
    """Casio fx-991CW Equation / Function Solver Dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Casio fx-991CW: Equation / Polynomial Solver")
        self.setMinimumWidth(460)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-family: monospace;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QComboBox {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("CASIO EQUATION SOLVER [Enter to calculate]")
        header.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "1: Quadratic Equation (ax² + bx + c = 0)",
            "2: Cubic Equation (ax³ + bx² + cx + d = 0)",
            "3: 2-Variable Linear System (a₁x + b₁y = c₁)",
            "4: Numerical Derivative d/dx at x = a",
            "5: Definite Integral ∫_a^b f(x) dx",
        ])
        self.mode_combo.currentIndexChanged.connect(self._update_fields)
        layout.addWidget(self.mode_combo)

        # Container for dynamic inputs
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.fields_container)

        # Solve button
        solve_btn = QPushButton("Calculate / Solve [Enter / EXE]")
        solve_btn.clicked.connect(self._on_solve)
        layout.addWidget(solve_btn)

        # Result display
        self.result_display = QLabel("Enter parameters above and click Solve or press Enter.")
        self.result_display.setStyleSheet("""
            background-color: #11111b;
            color: #a6e3a1;
            border: 1px solid #313244;
            border-radius: 8px;
            padding: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        """)
        self.result_display.setWordWrap(True)
        layout.addWidget(self.result_display)

        self._field_inputs: dict[str, QLineEdit] = {}
        self._update_fields(0)

    def _update_fields(self, index: int):
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._field_inputs.clear()

        fields = []
        if index == 0:  # Quadratic
            fields = [("a:", "1"), ("b:", "-5"), ("c:", "6")]
        elif index == 1:  # Cubic
            fields = [("a:", "1"), ("b:", "-6"), ("c:", "11"), ("d:", "-6")]
        elif index == 2:  # 2x2
            fields = [("a₁:", "2"), ("b₁:", "1"), ("c₁:", "5"),
                      ("a₂:", "1"), ("b₂:", "-1"), ("c₂:", "1")]
        elif index == 3:  # Derivative
            fields = [("f(x):", "x^3 - 2*x + 1"), ("at x =", "2.0")]
        elif index == 4:  # Integral
            fields = [("f(x):", "sin(x)"), ("Lower bound a:", "0"), ("Upper bound b:", "pi")]

        for label_text, default_val in fields:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(130)
            inp = QLineEdit(default_val)
            inp.returnPressed.connect(self._on_solve)  # Enter in any input triggers solve
            row.addWidget(lbl)
            row.addWidget(inp)
            self.fields_layout.addLayout(row)
            self._field_inputs[label_text] = inp

        if fields:
            first_key = fields[0][0]
            self._field_inputs[first_key].setFocus()
            self._field_inputs[first_key].selectAll()

    def _on_solve(self):
        idx = self.mode_combo.currentIndex()
        try:
            if idx == 0:  # Quadratic
                a = float(self._field_inputs["a:"].text())
                b = float(self._field_inputs["b:"].text())
                c = float(self._field_inputs["c:"].text())
                res = EquationSolver.solve_quadratic(a, b, c)
                if "error" in res:
                    self.result_display.setText(res["error"])
                else:
                    lines = [
                        f"Nature: {res['nature']}",
                        f"Roots:  x₁ = {res['roots'][0]},  x₂ = {res['roots'][1] if len(res['roots']) > 1 else res['roots'][0]}",
                        f"Vertex: ({res['vertex'][0]:.6g}, {res['vertex'][1]:.6g})",
                        f"Discriminant Δ = {res['discriminant']:.6g}",
                    ]
                    self.result_display.setText("\n".join(lines))

            elif idx == 1:  # Cubic
                a = float(self._field_inputs["a:"].text())
                b = float(self._field_inputs["b:"].text())
                c = float(self._field_inputs["c:"].text())
                d = float(self._field_inputs["d:"].text())
                res = EquationSolver.solve_cubic(a, b, c, d)
                roots_str = ", ".join(f"x_{i+1} = {r}" for i, r in enumerate(res["roots"]))
                self.result_display.setText(f"Cubic Roots:\n{roots_str}")

            elif idx == 2:  # 2x2
                a1 = float(self._field_inputs["a₁:"].text())
                b1 = float(self._field_inputs["b₁:"].text())
                c1 = float(self._field_inputs["c₁:"].text())
                a2 = float(self._field_inputs["a₂:"].text())
                b2 = float(self._field_inputs["b₂:"].text())
                c2 = float(self._field_inputs["c₂:"].text())
                res = EquationSolver.solve_linear_2x2(a1, b1, c1, a2, b2, c2)
                if "error" in res:
                    self.result_display.setText(res["error"])
                else:
                    self.result_display.setText(f"System Solution:\nx = {res['x']}\ny = {res['y']}\nDeterminant = {res['determinant']:.6g}")

            elif idx == 3:  # Derivative
                engine = CasioEngine()
                expr = self._field_inputs["f(x):"].text()
                val = float(self._field_inputs["at x ="].text())
                ok, d_res = engine.evaluate_derivative(expr, val)
                self.result_display.setText(f"d/dx [{expr}] |_(x={val}) =\n{d_res}")

            elif idx == 4:  # Integral
                engine = CasioEngine()
                expr = self._field_inputs["f(x):"].text()
                a_str = self._field_inputs["Lower bound a:"].text()
                b_str = self._field_inputs["Upper bound b:"].text()
                _, _, a_ev = engine.evaluate(a_str)
                _, _, b_ev = engine.evaluate(b_str)
                import sympy as sp
                a = float(sp.N(sp.sympify(a_ev or a_str)))
                b = float(sp.N(sp.sympify(b_ev or b_str)))
                ok, int_res = engine.evaluate_integral(expr, a, b)
                self.result_display.setText(f"∫ [{expr}] dx from {a:.4g} to {b:.4g} =\n{int_res}")

        except Exception as e:
            self.result_display.setText(f"Calculation Error: {e}")


class CasioWidget(QWidget):
    """Authentic Casio fx-991CW ClassWiz Scientific Calculator UI with Dual Mouse & Keyboard Operation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = CasioEngine()
        self._history: list[str] = []
        self._history_index: int = -1
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._init_ui()

    @property
    def current_formula(self) -> str:
        return self.formula_input.text()

    @current_formula.setter
    def current_formula(self, value: str):
        self.formula_input.setText(value)

    @property
    def formula_label(self):
        """Backward-compatibility alias pointing to formula_input."""
        return self.formula_input

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Authentically Styled Casio LCD Display Frame
        lcd_frame = QFrame()
        lcd_frame.setObjectName("CasioLCD")
        lcd_frame.setStyleSheet("""
            QFrame#CasioLCD {
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        lcd_layout = QVBoxLayout(lcd_frame)
        lcd_layout.setContentsMargins(8, 6, 8, 6)
        lcd_layout.setSpacing(4)

        # Status Bar: [DEG] [NATURAL-TEXTBOOK] [KEYBOARD ACTIVE] [S<=>D]
        status_bar = QHBoxLayout()
        self.mode_btn = QPushButton(f"[{self.engine.angle_mode}]")
        self.mode_btn.setToolTip("Click or press F2 to toggle angle mode (DEG -> RAD -> GRA)")
        self.mode_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.mode_btn.setStyleSheet("background: transparent; color: #58a6ff; font-weight: bold; font-family: monospace; font-size: 11px; border: none;")
        self.mode_btn.clicked.connect(self._toggle_angle_mode)
        status_bar.addWidget(self.mode_btn)

        math_badge = QLabel("[NATURAL-TEXTBOOK]")
        math_badge.setStyleSheet("color: #8b949e; font-size: 11px; font-family: monospace;")
        status_bar.addWidget(math_badge)

        kb_badge = QLabel("[⌨ KEYBOARD READY]")
        kb_badge.setToolTip("Full keyboard support: type expressions directly, Enter or '=' to solve, Tab for S<=>D, Up/Down for history, Esc to clear")
        kb_badge.setStyleSheet("color: #89dceb; font-size: 10px; font-family: monospace;")
        status_bar.addWidget(kb_badge)

        status_bar.addStretch()

        self.sd_badge = QLabel("[EXACT]")
        self.sd_badge.setStyleSheet("color: #3fb950; font-weight: bold; font-size: 11px; font-family: monospace;")
        status_bar.addWidget(self.sd_badge)

        lcd_layout.addLayout(status_bar)

        # Interactive Formula Input Line (Supports typing, pasting, cursor positioning, and button clicks)
        self.formula_input = CasioLineEdit(self)
        self.formula_input.setToolTip("Click or type directly with your keyboard. Press Enter or '=' to calculate.")
        self.formula_input.evaluate_requested.connect(self._evaluate)
        self.formula_input.ac_requested.connect(lambda: self._handle_key("AC"))
        self.formula_input.sd_requested.connect(self._toggle_sd)
        self.formula_input.history_prev_requested.connect(self._history_prev)
        self.formula_input.history_next_requested.connect(self._history_next)
        self.formula_input.angle_toggle_requested.connect(self._toggle_angle_mode)
        self.formula_input.solver_requested.connect(self._open_equation_solver)
        self.formula_input.constants_requested.connect(self._open_constants_menu)
        lcd_layout.addWidget(self.formula_input)

        # Result Line (Textbook Display)
        self.result_label = QLabel("0")
        self.result_label.setToolTip("Result display. Press Ctrl+C to copy.")
        self.result_label.setStyleSheet("color: #e6edf3; font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 30px; font-weight: bold; min-height: 42px;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lcd_layout.addWidget(self.result_label)

        main_layout.addWidget(lcd_frame)

        # Top Function Bar (Equation Solver, Constants, S<=>D)
        top_fn_bar = QHBoxLayout()
        solver_btn = QPushButton("EQUATION / SOLVE [F3]")
        solver_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        solver_btn.setStyleSheet("background-color: #21262d; color: #58a6ff; font-weight: bold; border-radius: 6px; padding: 6px 12px;")
        solver_btn.clicked.connect(self._open_equation_solver)
        top_fn_bar.addWidget(solver_btn)

        constants_btn = QPushButton("CONSTANTS [F4]")
        constants_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        constants_btn.setStyleSheet("background-color: #21262d; color: #d2a8ff; font-weight: bold; border-radius: 6px; padding: 6px 12px;")
        constants_btn.clicked.connect(self._open_constants_menu)
        top_fn_bar.addWidget(constants_btn)

        sd_btn = QPushButton("S ⇔ D [Tab]")
        sd_btn.setToolTip("Toggle between Exact Fraction/Radical and Decimal representation (Keyboard: Tab or Ctrl+D)")
        sd_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sd_btn.setStyleSheet("background-color: #1f6feb; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 6px 16px;")
        sd_btn.clicked.connect(self._toggle_sd)
        top_fn_bar.addWidget(sd_btn)

        main_layout.addLayout(top_fn_bar)

        # Casio Keypad Grid
        grid = QGridLayout()
        grid.setSpacing(5)

        # Buttons specification: (label, insert_text or action_type)
        # 6 columns layout replicating fx-991CW ClassWiz layout
        buttons_spec = [
            # Row 0: Scientific functions
            ("x²", "x²"), ("x^y", "^"), ("√", "√("), ("x⁻¹", "^(-1)"), ("log", "log10("), ("ln", "ln("),

            # Row 1: Trigonometric
            ("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("sin⁻¹", "asin("), ("cos⁻¹", "acos("), ("tan⁻¹", "atan("),

            # Row 2: Hyperbolic, Combinatorics, Abs
            ("sinh", "sinh("), ("cosh", "cosh("), ("tanh", "tanh("), ("nCr", "nCr"), ("nPr", "nPr"), ("x!", "!"),

            # Row 3: Brackets, Variable, Pi, e, Del, AC
            ("(", "("), (")", ")"), ("x", "x"), ("π", "π"), ("DEL", "DEL"), ("AC", "AC"),

            # Row 4: Numbers 7, 8, 9, ÷, %, sqrt(3)
            ("7", "7"), ("8", "8"), ("9", "9"), ("÷", "÷"), ("%", "/100"), ("i", "i"),

            # Row 5: Numbers 4, 5, 6, ×, gcd, lcm
            ("4", "4"), ("5", "5"), ("6", "6"), ("×", "×"), ("gcd", "gcd("), ("lcm", "lcm("),

            # Row 6: Numbers 1, 2, 3, −, Ans, Exp
            ("1", "1"), ("2", "2"), ("3", "3"), ("−", "−"), ("Ans", "Ans"), ("×10ˣ", "×10^"),

            # Row 7: 0, ., ±, +, =, S<=>D
            ("0", "0"), (".", "."), ("±", "NEG"), ("+", "+"), ("=", "EXEC"), ("S⇔D", "SD"),
        ]

        row = 0
        col = 0
        for label, action in buttons_spec:
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            # Distinct Casio Button Styling
            if label in ("AC", "DEL"):
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #8b1820;
                        color: #ffffff;
                        font-weight: bold;
                        border-radius: 6px;
                        font-size: 14px;
                        min-height: 38px;
                    }
                    QPushButton:hover { background-color: #a8202b; }
                """)
            elif label in ("=", "EXEC"):
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #238636;
                        color: #ffffff;
                        font-weight: bold;
                        border-radius: 6px;
                        font-size: 18px;
                        min-height: 38px;
                    }
                    QPushButton:hover { background-color: #2ea043; }
                """)
            elif label in ("+", "−", "×", "÷"):
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #21262d;
                        color: #58a6ff;
                        font-weight: bold;
                        border-radius: 6px;
                        font-size: 16px;
                        min-height: 38px;
                    }
                    QPushButton:hover { background-color: #30363d; }
                """)
            elif label.isdigit() or label == ".":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #161b22;
                        color: #f0f6fc;
                        font-weight: 600;
                        border-radius: 6px;
                        font-size: 16px;
                        min-height: 38px;
                    }
                    QPushButton:hover { background-color: #21262d; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #21262d;
                        color: #d2a8ff;
                        font-weight: 600;
                        border-radius: 6px;
                        font-size: 13px;
                        min-height: 38px;
                    }
                    QPushButton:hover { background-color: #30363d; }
                """)

            btn.clicked.connect(lambda _, a=action: self._handle_key(a))
            grid.addWidget(btn, row, col)

            col += 1
            if col == 6:
                col = 0
                row += 1

        main_layout.addLayout(grid)

    def focus_input(self):
        """Set active focus and cursor to formula input."""
        self.formula_input.setFocus()
        self.formula_input.setCursorPosition(len(self.formula_input.text()))

    def keyPressEvent(self, event):
        """Ensure all key events on CasioWidget route directly into formula input."""
        if not self.formula_input.hasFocus():
            self.formula_input.setFocus()
            self.formula_input.event(event)
        else:
            super().keyPressEvent(event)

    def _handle_key(self, action: str):
        if action == "AC":
            self.formula_input.clear()
            self.result_label.setText("0")
            self.sd_badge.setText("[EXACT]")
        elif action == "DEL":
            self.formula_input.backspace()
        elif action == "EXEC":
            self._evaluate()
        elif action == "SD":
            self._toggle_sd()
        elif action == "NEG":
            self.formula_input.insert("−")
        elif action == "x²":
            self.formula_input.insert("^2")
        else:
            self.formula_input.insert(action)

        self.formula_input.setFocus()

    def _evaluate(self):
        formula_text = self.formula_input.text().strip()
        if not formula_text:
            return

        # Record to history if distinct
        if not self._history or self._history[-1] != formula_text:
            self._history.append(formula_text)
        self._history_index = len(self._history)

        ok, res_str, _ = self.engine.evaluate(formula_text)
        self.result_label.setText(res_str)
        if ok:
            self.sd_badge.setText("[EXACT]" if not self.engine.display_as_decimal else "[DECIMAL]")
        self.formula_input.setFocus()

    def _toggle_sd(self):
        res = self.engine.toggle_exact_decimal()
        self.result_label.setText(res)
        self.sd_badge.setText("[DECIMAL]" if self.engine.display_as_decimal else "[EXACT]")
        self.formula_input.setFocus()

    def _toggle_angle_mode(self):
        modes = ["DEG", "RAD", "GRA"]
        curr_idx = modes.index(self.engine.angle_mode)
        new_mode = modes[(curr_idx + 1) % len(modes)]
        self.engine.set_angle_mode(new_mode)
        self.mode_btn.setText(f"[{new_mode}]")
        if self.formula_input.text().strip():
            self._evaluate()
        self.formula_input.setFocus()

    def _history_prev(self):
        """Recall previous expression from calculation history (Up Arrow)."""
        if not self._history:
            return
        if self._history_index > 0:
            self._history_index -= 1
        elif self._history_index == -1 or self._history_index >= len(self._history):
            self._history_index = len(self._history) - 1
        self.formula_input.setText(self._history[self._history_index])
        self.formula_input.setCursorPosition(len(self.formula_input.text()))

    def _history_next(self):
        """Recall next expression from calculation history (Down Arrow)."""
        if not self._history:
            return
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.formula_input.setText(self._history[self._history_index])
            self.formula_input.setCursorPosition(len(self.formula_input.text()))
        else:
            self._history_index = len(self._history)
            self.formula_input.clear()

    def _open_equation_solver(self):
        dlg = EquationSolverDialog(self)
        dlg.exec()
        self.formula_input.setFocus()

    def _open_constants_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; font-family: monospace;")
        for cname, (cval, cdesc) in CasioEngine.CONSTANTS.items():
            act = QAction(f"{cname} : {cdesc} ({cval:.4e})", self)
            act.triggered.connect(lambda _, n=cname: self._insert_constant(n))
            menu.addAction(act)
        menu.exec(self.mapToGlobal(self.rect().center()))
        self.formula_input.setFocus()

    def _insert_constant(self, name: str):
        self.formula_input.insert(name)
        self.formula_input.setFocus()
