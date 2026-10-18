# Casio fx-991CW & Desmos Graphing Suite

An advanced, 100% offline scientific and graphing calculator desktop application. Built with **PyQt6**, **SymPy**, **pyqtgraph**, **NumPy**, and **Manim Community**.

Combines the textbook symbolic math precision of the **Casio fx-991CW ClassWiz** with the 60 FPS fluid interactive 2D curve plotting of **Desmos**, plus an integrated **Manim 3Blue1Brown Animation Studio**.

---

## Key Features

### 📟 1. Casio fx-991CW ClassWiz Scientific Mode
- **Natural Textbook Display**: Formats exact fractions ($\frac{a}{b}$), radicals ($\sqrt{x}$), powers ($x^y$), and constants ($\pi, e, i$).
- **Authentic $S \Leftrightarrow D$ Key**: Instantly toggle between exact symbolic math (surd/fraction) and decimal representation with one click.
- **Angle Modes**: Real-time switching between `[DEG]`, `[RAD]`, and `[GRA]`.
- **Calculus Engine**:
  - Numerical and symbolic derivatives: $\left.\frac{d}{dx}f(x)\right|_{x=a}$
  - Definite integrals: $\int_a^b f(x) dx$
- **Polynomial & Simultaneous Equation Solver**:
  - Quadratic equations ($ax^2 + bx + c = 0$ with discriminant, vertex, real/complex roots)
  - Cubic equations ($ax^3 + bx^2 + cx + d = 0$)
  - $2 \times 2$ and $3 \times 3$ linear systems of equations
- **Physical Scientific Constants**: One-click insertion of standard physical constants ($c, h, G, N_A, k_B, q_e, m_e, m_p, R, g$).
- **Combinatorics & Algebra**: $nCr, nPr, x!, \text{gcd}, \text{lcm}, \text{abs}, \ln, \log_{10}, \log_b(a)$.

### 📈 2. Desmos-Style Interactive 2D Graphing Mode
- **Hardware-Accelerated 60 FPS Canvas**: Ultra-smooth pan and zoom powered by `pyqtgraph`.
- **Multi-Curve Expression Manager**:
  - Plot multiple expressions simultaneously ($f_1(x) = \sin(x)$, $f_2(x) = 0.2x^2 - 3$, etc.).
  - Distinct vibrant neon curve colors.
  - Individual curve visibility checkboxes and delete controls.
- **Dynamic Parameter Sliders**: Real-time evaluation of parametric variables (e.g., $a \cdot \sin(b \cdot x)$) as sliders move.
- **Interactive Coordinate Tracker**: Crosshair cursor tracks mouse movement with live $(x, y)$ readout.
- **Curve Analysis**:
  - **Root Finder**: Automatically detects all real roots ($f(x) = 0$) in the visible range and places visual markers.
  - **Extrema Finder**: Computes local minima and maxima with coordinates.
  - **Definite Area Integration**: Fast trapezoidal/Simpson numerical integration under the curve.

### 🎬 3. Manim Animation Studio (3Blue1Brown Scene Exporter)
- Export your active Desmos function curves into a ready-to-run **Manim Community** animation script (`scene.py`).
- Integrated offline video renderer: Render smooth 60 FPS mathematical animations (MP4) directly from the application!

---

## Project Structure

```
CalculatorApp/
├── .venv/                         # Self-contained Python virtual environment
├── pyproject.toml                 # Standard PEP 518/621 packaging metadata
├── requirements.txt               # Pinned dependencies
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
├── README.md                      # Documentation
├── run.sh                         # Direct launcher (auto-activates .venv)
├── calculator-app.desktop         # Linux desktop entry
├── assets/
│   └── calculator-app.svg         # Scalable vector application icon
├── src/
│   ├── main.py                    # Main application window & tab switcher
│   ├── styles.py                  # Dark neon aesthetic stylesheet
│   ├── casio/
│   │   ├── casio_engine.py        # SymPy symbolic engine & constant database
│   │   ├── casio_widget.py        # Casio LCD display & keypad UI
│   │   └── equation_solver.py     # Polynomial & linear system solver
│   ├── desmos/
│   │   ├── graph_canvas.py        # 60 FPS pyqtgraph interactive plotting canvas
│   │   ├── desmos_widget.py       # Function sidebar, sliders, and controls
│   │   └── analysis.py            # Roots, extrema, and numerical integration
│   └── manim_studio/
│       └── manim_exporter.py      # 3Blue1Brown Manim script generator & MP4 renderer
└── tests/
    ├── test_casio_engine.py       # Casio math engine test suite
    ├── test_equation_solver.py    # Equation solver test suite
    └── test_desmos_evaluator.py   # Curve analysis test suite
```

---

## Installation & Quick Start

### 1. Launch with Pre-Configured Virtualenv
The virtual environment is already prepared in `.venv/`. Simply run:

```bash
./run.sh
```

### 2. Manual Setup from Scratch (For GitHub Clones)

```bash
# Clone the repository
git clone https://github.com/your-username/casio-desmos-calculator.git
cd casio-desmos-calculator

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

---

## Running the Automated Test Suite

Run the full suite of unit tests:

```bash
.venv/bin/python -m unittest discover -s tests
```

---

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + 1` | Switch to **Casio fx-991CW Scientific** mode |
| `Ctrl + 2` | Switch to **Desmos Graphing** mode |
| `F11` | Toggle Fullscreen mode |
| `Enter` / `=` | Evaluate expression in Casio mode |
| `Esc` | All Clear (`AC`) in Casio mode |
| `Delete` | Clear Entry (`CE`) in Casio mode |
| `Backspace` | Delete last entered character |

---

## License

This project is licensed under the [MIT License](LICENSE).
