"""Modern Dark & Neon Theme for Casio + Desmos + Manim Suite."""

MAIN_THEME = """
/* Main Window */
QMainWindow#MainWindow {
    background-color: #11111b;
}

/* Tab Bar */
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #181825;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #1e1e2e;
    color: #a6adc8;
    font-family: 'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', sans-serif;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 24px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    border: 1px solid #313244;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #181825;
    color: #89b4fa;
    border-top: 2px solid #89b4fa;
}

QTabBar::tab:hover:!selected {
    background-color: #313244;
    color: #cdd6f4;
}

/* Tooltips */
QToolTip {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #181825;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
