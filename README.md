# Casio fx-991CW & Desmos Graphing Suite

An advanced, 100% offline scientific and graphing calculator desktop application. Built with **PyQt6**, **SymPy**, **pyqtgraph**, and **NumPy**.

Combines the textbook symbolic math precision of the **Casio fx-991CW ClassWiz** with the 60 FPS fluid interactive 2D curve plotting of **Desmos**, featuring **Dynamic Parameter Sliders** and comprehensive keyboard navigation.

---

## Key Features

### 📟 1. Casio fx-991CW ClassWiz Scientific Mode
- **Natural Textbook Display**: Formats exact fractions ($\frac{a}{b}$), radicals ($\sqrt{x}$), powers ($x^y$), and constants ($\pi, e, i$).
- **Full Keyboard-First Navigation**: Type formulas directly on your physical keyboard with an active blinking cursor, selection, and clipboard support.
- **Authentic $S \Leftrightarrow D$ Key**: Instantly toggle between exact symbolic math (surd/fraction) and decimal representation with one click or `[Tab]`.
- **Calculation History**: Step backwards and forwards through previous calculations using `[↑]` and `[↓]` arrow keys.
- **Angle Modes**: Real-time switching between `[DEG]`, `[RAD]`, and `[GRA]` (Hotkey: `[F2]`).
- **Calculus Engine**:
  - Numerical and symbolic derivatives: $\left.\frac{d}{dx}f(x)\right|_{x=a}$
  - Definite integrals: $\int_a^b f(x) dx$
- **Polynomial & Simultaneous Equation Solver** (`[F3]`):
  - Quadratic equations ($ax^2 + bx + c = 0$ with discriminant, vertex, real/complex roots)
  - Cubic equations ($ax^3 + bx^2 + cx + d = 0$)
  - $2 \times 2$ and $3 \times 3$ linear systems of equations
- **Physical Scientific Constants** (`[F4]`): One-click insertion of standard physical constants ($c, h, G, N_A, k_B, q_e, m_e, m_p, R, g$).
- **Combinatorics & Algebra**: $nCr, nPr, x!, \text{gcd}, \text{lcm}, \text{abs}, \ln, \log_{10}, \log_b(a)$.

### 📈 2. Desmos-Style Interactive 2D Graphing Mode
- **Hardware-Accelerated 60 FPS Canvas**: Ultra-smooth continuous pan and zoom powered by `pyqtgraph`.
- **Multi-Curve Expression Manager**:
  - Plot multiple expressions simultaneously ($f_1(x) = \sin(x)$, $f_2(x) = 0.2x^2 - 3$, etc.).
  - Distinct vibrant neon curve colors.
  - Individual curve visibility checkboxes and delete controls.
  - Press `[Enter]` on any row to advance or create new expression rows.
- **Dynamic Parameter Sliders (Custom Parameters)**:
  - Add and use custom parameters ($a, b, c, k, m, \omega, \dots$) in any expression ($f(x) = a \cdot \sin(b \cdot x + c)$).
  - Click **"+ Add Slider"** (`[Ctrl+P]`) to create new variables with custom min/max bounds and initial values.
  - Dual control: drag the horizontal slider for continuous 60 FPS animation or type precise values into the numerical spinbox.
  - Delete individual parameter sliders at any time.
- **Interactive Coordinate Tracker**: Crosshair cursor tracks mouse movement with live $(x, y)$ readout.
- **Curve Analysis**:
  - **Root Finder**: Automatically detects all real roots ($f(x) = 0$) in the visible range and places visual markers.
  - **Extrema Finder**: Computes local minima and maxima with coordinates.
  - **Definite Area Integration**: Fast trapezoidal/Simpson numerical integration under the curve.
- **Common Functions Library**: 20+ categorized mathematical presets (Trigonometric, Polynomials, Exponential, Parametric).

---

## Project Structure

```
CalculatorApp/
├── .venv/                         # Self-contained Python virtual environment
├── pyproject.toml                 # Standard PEP 518/621 packaging metadata
├── requirements.txt               # Pinned dependencies
├── .gitignore                     # Git ignore rules
├── LICENSE                        # Apache 2.0 License
├── README.md                      # Documentation
├── run.sh                         # Direct launcher (auto-activates .venv)
├── build_app.sh                   # PyInstaller standalone builder
├── PKGBUILD                       # Arch/Garuda Linux native package script
├── calculator-app.desktop         # Linux desktop entry
├── assets/
│   └── calculator-app.svg         # Scalable vector application icon
├── src/
│   ├── main.py                    # Main application window & tab switcher
│   ├── styles.py                  # Dark neon aesthetic stylesheet
│   ├── casio/
│   │   ├── casio_engine.py        # SymPy symbolic engine & constant database
│   │   ├── casio_widget.py        # Casio LCD display, keypad UI & keyboard handler
│   │   └── equation_solver.py     # Polynomial & linear system solver
│   └── desmos/
│       ├── graph_canvas.py        # 60 FPS pyqtgraph interactive plotting canvas
│       ├── desmos_widget.py       # Function sidebar, dynamic sliders, and controls
│       └── analysis.py            # Roots, extrema, and numerical integration
└── tests/
    ├── test_calc.py               # Calculator basic unit tests
    ├── test_casio_engine.py       # Casio math engine test suite
    ├── test_equation_solver.py    # Equation solver test suite
    ├── test_desmos_evaluator.py   # Curve analysis test suite
    ├── test_keyboard_input.py     # Full keyboard input and shortcut tests
    └── test_dynamic_parameters.py # Dynamic parameter slider test suite
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
git clone https://github.com/lucifer-0-0-1/Graphing-Calculator.git
cd Graphing-Calculator

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

## Building & Packaging as an App

Choose the build method best suited for your distribution or packaging workflow:

### Option 1: Standalone Linux Executable Directory (PyInstaller)
Bundles Python, PyQt6, NumPy, SymPy, pyqtgraph, and all dependencies into a portable directory that runs on any modern 64-bit Linux distribution without needing Python installed:

```bash
./build_app.sh
```
- **Output Executable**: `dist/calculator-suite/calculator-suite`
- **To Launch**: `./dist/calculator-suite/calculator-suite`
- You can distribute this `dist/calculator-suite` folder to any other Linux machine.

---

### Option 2: Native Arch / Garuda Linux Package (`.pkg.tar.zst`)
Builds a native package managed by `pacman`. Packages the self-contained app into `/usr/lib/calculator-suite`, symlinks `/usr/bin/calculator-app`, and installs standard KDE Plasma desktop entries and icons:

```bash
# 1. Build the package
makepkg -f

# 2. Install system-wide with pacman
sudo pacman -U calculator-app-1.0.0-1-x86_64.pkg.tar.zst
```

---

### Option 3: Standard Python Package CLI Tool (`pipx` / `pip`)
Because `pyproject.toml` is configured, you can install the app directly into your user environment:

```bash
# Install with pipx (recommended for isolated CLI tools):
pipx install .

# Or with pip in editable mode:
pip install -e .
```
This registers the global command:
```bash
casio-desmos-calc
```

---

## Keyboard Shortcuts & Desktop Controls

The application is engineered for complete keyboard-first operation without needing a mouse:

| Key / Shortcut | Context | Action |
| :--- | :--- | :--- |
| **`0` – `9`, `+`, `-`, `*`, `/`, `^`, `(`, `)`** | Casio Mode | Direct mathematical typing with active blinking cursor |
| **`Enter` / `Return` / `=`** | Casio Mode | Calculate / Evaluate expression (`[EXE]`) |
| **`Esc`** | Casio Mode | All Clear (`[AC]`) — resets display to 0 |
| **`Tab`** or **`Ctrl + D`** | Casio Mode | Toggle Exact $\Leftrightarrow$ Decimal representation (`[S ⇔ D]`) |
| **`↑` (Up Arrow)** | Casio Mode | Recall previous calculation from history |
| **`↓` (Down Arrow)** | Casio Mode | Recall next calculation from history |
| **`F2`** | Casio Mode | Toggle Angle Mode (`[DEG]` $\rightarrow$ `[RAD]` $\rightarrow$ `[GRA]`) |
| **`F3`** or **`Ctrl + E`** | Casio Mode | Open Polynomial & Simultaneous Equation Solver |
| **`F4`** or **`Ctrl + P`** | Casio Mode | Open Physical Scientific Constants menu ($c, h, G, \dots$) |
| **`Ctrl + C`** | Casio Mode | Copy result value to system clipboard |
| **`Enter`** | Desmos Rows | Move to next expression row or create a new row |
| **`Ctrl + N`** | Desmos Mode | Add a new function row |
| **`Ctrl + P`** | Desmos Mode | Add a new dynamic parameter slider |
| **`Ctrl + R`** | Desmos Mode | Reset graph pan and zoom view |
| **`Ctrl + 1`** | Universal | Switch to **Casio Scientific** mode and focus input |
| **`Ctrl + 2`** | Universal | Switch to **Desmos Graphing** mode and focus input |
| **`F11`** | Universal | Toggle Fullscreen mode |

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
