#!/bin/bash
# Script to activate the virtual environment

source "$(dirname "$0")/venv/bin/activate"
echo "Virtual environment activated!"
echo "Python: $(which python)"
echo "To deactivate, run: deactivate"

