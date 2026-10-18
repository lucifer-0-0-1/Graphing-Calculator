"""Manim Math Animation Studio & Code Generator (LaTeX-Free Offline Rendering)."""
import os
import subprocess
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class ManimRenderWorker(QThread):
    """Background worker thread to render Manim video animations without freezing UI."""

    progress_log = pyqtSignal(str)
    render_finished = pyqtSignal(bool, str)

    def __init__(self, script_path: str, output_dir: str):
        super().__init__()
        self.script_path = script_path
        self.output_dir = output_dir

    def run(self):
        # Locate venv python/manim
        venv_manim = Path(__file__).resolve().parent.parent.parent / ".venv" / "bin" / "manim"
        manim_cmd = str(venv_manim) if venv_manim.exists() else "manim"

        cmd = [
            manim_cmd,
            "render",
            "-ql",  # Quick 480p preview for fast rendering
            "--media_dir", self.output_dir,
            self.script_path,
            "GraphAnimationScene",
        ]

        self.progress_log.emit(f"Starting Manim render: {' '.join(cmd)}\n")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(Path(self.script_path).parent),
            )

            for line in iter(process.stdout.readline, ''):
                self.progress_log.emit(line)

            process.stdout.close()
            ret = process.wait()

            if ret == 0:
                self.render_finished.emit(True, "Animation rendered successfully!")
            else:
                self.render_finished.emit(False, f"Manim exited with code {ret}")
        except Exception as e:
            self.render_finished.emit(False, f"Render failed: {e}")


class ManimStudioDialog(QDialog):
    """Interactive Manim code generator and offline video renderer."""

    def __init__(self, functions: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.functions = functions  # List of (expr_str, hex_color)
        self.setWindowTitle("Manim Mathematical Animation Studio (Offline)")
        self.resize(720, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-family: monospace;
            }
            QTextEdit {
                background-color: #11111b;
                color: #a6e3a1;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 10px;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 12px;
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

        header = QLabel("MANIM SCENE GENERATOR (3Blue1Brown Offline Animation)")
        header.setStyleSheet("color: #fab387; font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        info = QLabel("Export and render smooth mathematical animations of your plotted functions without LaTeX.")
        info.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(info)

        # Code display
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText(self._generate_manim_script())
        layout.addWidget(self.code_edit, stretch=3)

        # Progress / Output Log
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText("Manim render logs will appear here...")
        self.log_edit.setStyleSheet("background-color: #181825; color: #89dceb; font-size: 11px;")
        layout.addWidget(self.log_edit, stretch=2)

        # Action buttons
        btn_bar = QHBoxLayout()

        save_btn = QPushButton("💾 Save Scene (.py)")
        save_btn.clicked.connect(self._save_script)
        btn_bar.addWidget(save_btn)

        self.render_btn = QPushButton("🎬 Render Animation (MP4)")
        self.render_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 8px 20px;")
        self.render_btn.clicked.connect(self._start_render)
        btn_bar.addWidget(self.render_btn)

        layout.addLayout(btn_bar)

        self.worker: ManimRenderWorker = None

    def _generate_manim_script(self) -> str:
        """Generate standalone Manim Community Python script without LaTeX dependency."""
        curve_defs = []
        play_items = ["Create(axes)"]

        color_map = {
            "#00d2ff": "TEAL_A",
            "#ff007f": "MAROON_A",
            "#39ff14": "GREEN_A",
            "#ffea00": "YELLOW_A",
            "#bb9af7": "PURPLE_A",
            "#ff9e64": "GOLD_A",
            "#2ac3de": "BLUE_B",
        }

        for i, (expr, hex_color) in enumerate(self.functions):
            # Python lambda conversion
            clean_expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
            clean_expr = clean_expr.replace("sin", "np.sin").replace("cos", "np.cos")
            clean_expr = clean_expr.replace("tan", "np.tan").replace("sqrt", "np.sqrt").replace("exp", "np.exp")
            clean_expr = clean_expr.replace("ln", "np.log").replace("abs", "np.abs")

            color_name = color_map.get(hex_color.lower(), "BLUE_B")
            fn_name = f"graph_{i+1}"
            lbl_name = f"label_{i+1}"

            curve_defs.append(f"""
        # Curve {i+1}: f(x) = {expr}
        {fn_name} = axes.plot(
            lambda x: {clean_expr},
            color={color_name},
            x_range=[-7, 7],
            use_smoothing=True
        )
        {lbl_name} = Text("f_{i+1}(x) = {expr}", font_size=18, color={color_name}).next_to({fn_name}, UP, buff=0.2)
            """)
            play_items.append(f"Create({fn_name})")
            play_items.append(f"Write({lbl_name})")

        plots_block = "\n".join(curve_defs)
        play_block = ", ".join(play_items)

        script = f'''"""Generated 3Blue1Brown-style Math Animation Scene using Manim."""
from manim import *
import numpy as np

class GraphAnimationScene(Scene):
    def construct(self):
        # 1. Setup Cartesian Axes (Using Text labels for 100% offline rendering without LaTeX)
        axes = Axes(
            x_range=[-8, 8, 2],
            y_range=[-5, 5, 1],
            x_length=10,
            y_length=6,
            axis_config={{"color": GREY_A, "stroke_width": 2}},
            tips=True,
        )
        # Use Text instead of LaTeX to avoid external compiler dependency
        axes.add_coordinates(label_constructor=Text, font_size=16)

        title = Text("Desmos & Casio Graph Visualization", font_size=26, color=BLUE_B).to_edge(UP)

        self.play(Write(title))
{plots_block}

        # 2. Animate coordinate axes and mathematical curves
        self.play({play_block}, run_time=3.0)
        self.wait(2)
'''
        return script

    def _save_script(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Manim Scene", str(Path.home() / "scene.py"), "Python Files (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.code_edit.toPlainText())
            QMessageBox.information(self, "Saved", f"Manim scene saved to:\n{path}")

    def _start_render(self):
        temp_dir = tempfile.mkdtemp(prefix="manim_calc_")
        script_file = os.path.join(temp_dir, "scene.py")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(self.code_edit.toPlainText())

        self.log_edit.clear()
        self.render_btn.setEnabled(False)
        self.render_btn.setText("Rendering...")

        self.worker = ManimRenderWorker(script_file, temp_dir)
        self.worker.progress_log.connect(self._append_log)
        self.worker.render_finished.connect(self._on_render_finished)
        self.worker.start()

    def _append_log(self, text: str):
        self.log_edit.append(text.rstrip())

    def _on_render_finished(self, success: bool, message: str):
        self.render_btn.setEnabled(True)
        self.render_btn.setText("🎬 Render Animation (MP4)")
        if success:
            QMessageBox.information(self, "Render Complete", f"{message}\n\nMedia generated in directory:\n{self.worker.output_dir}")
        else:
            QMessageBox.warning(self, "Render Issue", message)
