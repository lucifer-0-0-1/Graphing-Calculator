#!/usr/bin/env bash
set -e

# Standalone App Builder using PyInstaller
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "${SCRIPT_DIR}/.venv/bin/pyinstaller" ]; then
    echo "Error: PyInstaller not found in .venv. Run 'uv pip install --python .venv pyinstaller' first."
    exit 1
fi

echo "=========================================================="
echo " Building Standalone Linux Application: Calculator Suite"
echo "=========================================================="

"${SCRIPT_DIR}/.venv/bin/pyinstaller" \
    --name "calculator-suite" \
    --windowed \
    --onedir \
    --add-data "${SCRIPT_DIR}/assets:assets" \
    --icon "${SCRIPT_DIR}/assets/calculator-app.svg" \
    --clean \
    --noconfirm \
    "${SCRIPT_DIR}/src/main.py"

echo ""
echo "=========================================================="
echo " Build Complete!"
echo " Standalone App Directory: ${SCRIPT_DIR}/dist/calculator-suite/"
echo " Executable Binary:        ${SCRIPT_DIR}/dist/calculator-suite/calculator-suite"
echo "=========================================================="
