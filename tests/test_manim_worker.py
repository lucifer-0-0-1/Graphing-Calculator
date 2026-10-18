"""Unit tests for Manim Studio script generator and render worker."""
import unittest
import os
import tempfile
from PyQt6.QtWidgets import QApplication
from src.manim_studio.manim_exporter import ManimStudioDialog, ManimRenderWorker

# Headless Qt app instance for test suite
_app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])


class TestManimStudio(unittest.TestCase):
    def setUp(self):
        self.dialog = ManimStudioDialog([("sin(x)", "#00d2ff"), ("x^2 - 4", "#ff007f")])

    def test_script_generation(self):
        script = self.dialog._generate_manim_script()
        self.assertIn("class GraphAnimationScene(Scene):", script)
        self.assertIn("np.sin(x)", script)
        self.assertIn("x**2 - 4", script)
        self.assertIn("axes.add_coordinates(label_constructor=Text", script)
        self.assertIn("label_1 = Text(", script)
        self.assertIn("label_2 = Text(", script)

    def test_worker_initialization(self):
        temp_dir = tempfile.mkdtemp()
        script_file = os.path.join(temp_dir, "scene.py")
        code = self.dialog._generate_manim_script()
        worker = ManimRenderWorker(script_file, temp_dir, code)
        self.assertEqual(worker.script_path, script_file)
        self.assertEqual(worker.output_dir, temp_dir)
        self.assertEqual(worker.code_content, code)


if __name__ == "__main__":
    unittest.main()
