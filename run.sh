#!/usr/bin/env bash
# Direct launcher for development and local testing
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

if [ -f "${SCRIPT_DIR}/.venv/bin/python" ]; then
    PYTHON_BIN="${SCRIPT_DIR}/.venv/bin/python"
else
    PYTHON_BIN="$(which python3)"
fi

exec "${PYTHON_BIN}" "${SCRIPT_DIR}/src/main.py" "$@"
