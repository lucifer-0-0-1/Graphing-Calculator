#!/usr/bin/env bash
export PYTHONPATH="/usr/share/calculator-app:${PYTHONPATH}"
exec /usr/bin/python3 /usr/share/calculator-app/src/main.py "$@"
