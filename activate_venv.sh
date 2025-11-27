#!/bin/bash
# Script to activate the training virtual environment

source "$(dirname "$0")/venv/bin/activate"
echo "Training virtual environment activated!"
echo "Python: $(which python)"
echo "To deactivate, run: deactivate"
echo ""
echo "To train the model, run:"
echo "  python train_and_save_model.py"

