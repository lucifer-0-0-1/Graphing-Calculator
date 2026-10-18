"""Unit tests for keyboard input, navigation, shortcuts, and history."""
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent

from src.casio.casio_widget import CasioWidget
from src.desmos.desmos_widget import DesmosWidget

_app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])


class TestKeyboardInput(unittest.TestCase):
    def setUp(self):
        self.casio = CasioWidget()
        self.desmos = DesmosWidget()

    def _send_key(self, widget, key, text="", modifiers=Qt.KeyboardModifier.NoModifier):
        event = QKeyEvent(QEvent.Type.KeyPress, key, modifiers, text)
        QApplication.sendEvent(widget, event)

    def test_direct_typing_and_evaluation(self):
        # Type "15+27" then press Enter
        self.casio.formula_input.setText("15+27")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Return)
        self.assertEqual(self.casio.result_label.text(), "42")

    def test_equal_key_evaluates(self):
        self.casio.formula_input.setText("8 * 9")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Equal, text="=")
        self.assertEqual(self.casio.result_label.text(), "72")

    def test_escape_clears(self):
        self.casio.formula_input.setText("12345")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Escape)
        self.assertEqual(self.casio.formula_input.text(), "")
        self.assertEqual(self.casio.result_label.text(), "0")

    def test_tab_toggles_sd(self):
        self.casio.formula_input.setText("3/4")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Return)
        self.assertEqual(self.casio.result_label.text(), "3/4")
        # Press Tab
        self._send_key(self.casio.formula_input, Qt.Key.Key_Tab)
        self.assertEqual(self.casio.result_label.text(), "0.75")
        # Press Tab again
        self._send_key(self.casio.formula_input, Qt.Key.Key_Tab)
        self.assertEqual(self.casio.result_label.text(), "3/4")

    def test_history_arrow_navigation(self):
        # Perform two calculations
        self.casio.formula_input.setText("2 + 2")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Return)
        self.casio.formula_input.setText("sqrt(144)")
        self._send_key(self.casio.formula_input, Qt.Key.Key_Return)

        # Press Up Arrow -> recalls last formula
        self._send_key(self.casio.formula_input, Qt.Key.Key_Up)
        self.assertEqual(self.casio.formula_input.text(), "sqrt(144)")

        # Press Up Arrow again -> recalls first formula
        self._send_key(self.casio.formula_input, Qt.Key.Key_Up)
        self.assertEqual(self.casio.formula_input.text(), "2 + 2")

        # Press Down Arrow -> moves forward
        self._send_key(self.casio.formula_input, Qt.Key.Key_Down)
        self.assertEqual(self.casio.formula_input.text(), "sqrt(144)")

    def test_f2_toggles_angle_mode(self):
        initial_mode = self.casio.engine.angle_mode
        self._send_key(self.casio.formula_input, Qt.Key.Key_F2)
        self.assertNotEqual(self.casio.engine.angle_mode, initial_mode)

    def test_operator_auto_replace(self):
        # When typing '*' or '/', replaces with authentic Casio glyphs
        self.casio.formula_input.clear()
        self._send_key(self.casio.formula_input, Qt.Key.Key_Asterisk, text="*")
        self.assertEqual(self.casio.formula_input.text(), "×")

        self.casio.formula_input.clear()
        self._send_key(self.casio.formula_input, Qt.Key.Key_Slash, text="/")
        self.assertEqual(self.casio.formula_input.text(), "÷")

    def test_desmos_enter_adds_or_advances_row(self):
        initial_count = len(self.desmos.functions)
        last_id = list(self.desmos.functions.keys())[-1]
        last_row = self.desmos.functions[last_id]

        # Pressing Return in last row creates new row
        self._send_key(last_row.input_edit, Qt.Key.Key_Return)
        self.assertEqual(len(self.desmos.functions), initial_count + 1)


if __name__ == "__main__":
    unittest.main()
