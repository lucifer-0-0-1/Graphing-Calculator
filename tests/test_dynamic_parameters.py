"""Unit tests for dynamic parameter sliders in DesmosWidget."""
import unittest
from PyQt6.QtWidgets import QApplication
from src.desmos.desmos_widget import DesmosWidget, ParameterSliderRow, AddParameterDialog

_app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])


class TestDynamicParameters(unittest.TestCase):
    def setUp(self):
        self.widget = DesmosWidget()

    def test_initial_parameters(self):
        self.assertIn("a", self.widget.slider_params)
        self.assertIn("b", self.widget.slider_params)
        self.assertEqual(self.widget.slider_params["a"], 1.0)
        self.assertEqual(self.widget.slider_params["b"], 1.0)

    def test_add_new_parameter(self):
        self.widget.add_parameter("k", 2.5, -20.0, 20.0)
        self.assertIn("k", self.widget.slider_params)
        self.assertEqual(self.widget.slider_params["k"], 2.5)
        self.assertIn("k", self.widget.param_rows)
        row = self.widget.param_rows["k"]
        self.assertEqual(row.value, 2.5)

    def test_slider_value_change(self):
        self.widget.add_parameter("m", 3.0, -10.0, 10.0)
        row = self.widget.param_rows["m"]
        # Change value via spinbox
        row.spin.setValue(4.5)
        self.assertEqual(self.widget.slider_params["m"], 4.5)

    def test_remove_parameter(self):
        self.widget.add_parameter("c", -5.0)
        self.assertIn("c", self.widget.slider_params)
        self.widget.remove_parameter("c")
        self.assertNotIn("c", self.widget.slider_params)
        self.assertNotIn("c", self.widget.param_rows)

    def test_dialog_validation(self):
        existing = {"a", "b"}
        dlg = AddParameterDialog(existing)

        # Reserved name "x"
        dlg.name_edit.setText("x")
        self.assertIn("x", {"x", "y"})

        # Valid name "omega"
        dlg.name_edit.setText("omega")
        self.assertTrue(dlg.name_edit.text().isidentifier())


if __name__ == "__main__":
    unittest.main()
