"""Main Application Entry Point: Casio fx-991CW + Desmos Graphing + Manim Studio."""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

from src.styles import MAIN_THEME
from src.casio.casio_widget import CasioWidget
from src.desmos.desmos_widget import DesmosWidget
from src.manim_studio.manim_exporter import ManimStudioDialog


class AdvancedCalculatorApp(QMainWindow):
    """Unified Advanced Scientific and Graphing Calculator Window."""

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Casio fx-991CW & Desmos Graphing Suite")
        self.setMinimumSize(960, 680)
        self.resize(1100, 780)

        self._setup_icon()
        self._init_ui()
        self._setup_shortcuts()

    def _setup_icon(self):
        """Locate and set application icon."""
        base_dir = Path(__file__).resolve().parent.parent
        local_icon = base_dir / "assets" / "calculator-app.svg"
        system_icon = Path("/usr/share/icons/hicolor/scalable/apps/calculator-app.svg")

        if local_icon.exists():
            self.setWindowIcon(QIcon(str(local_icon)))
        elif system_icon.exists():
            self.setWindowIcon(QIcon(str(system_icon)))

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Mode 1: Casio fx-991CW Scientific ClassWiz
        self.casio_tab = CasioWidget(self)
        self.tabs.addTab(self.casio_tab, "📟 Casio fx-991CW (Scientific)")

        # Mode 2: Desmos Graphing Calculator
        self.desmos_tab = DesmosWidget(self)
        self.desmos_tab.request_manim_export.connect(self._open_manim_studio)
        self.tabs.addTab(self.desmos_tab, "📈 Desmos (Graphing & Sliders)")

        layout.addWidget(self.tabs)

    def _setup_shortcuts(self):
        """Configure keyboard navigation shortcuts."""
        # Switch tabs via Ctrl+1, Ctrl+2
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.tabs.setCurrentIndex(1))

        # Fullscreen toggle F11
        f11 = QShortcut(QKeySequence("F11"), self)
        f11.activated.connect(self._toggle_fullscreen)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _open_manim_studio(self, functions: list):
        """Open the Manim Animation Studio dialog with the active curves."""
        dlg = ManimStudioDialog(functions, self)
        dlg.exec()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("CasioDesmosCalculator")
    app.setDesktopFileName("calculator-app")
    app.setStyleSheet(MAIN_THEME)

    window = AdvancedCalculatorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
