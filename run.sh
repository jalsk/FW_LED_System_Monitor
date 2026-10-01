#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# A distro upgrade that bumps python3 strands the venv on a removed interpreter.
PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [ -d "$VENV_DIR" ] && ! grep -q "^version = $PY_VER\." "$VENV_DIR/pyvenv.cfg" 2>/dev/null; then
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

python "$SCRIPT_DIR/led_system_monitor.py"
