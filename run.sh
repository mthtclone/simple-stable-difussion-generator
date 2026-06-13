#!/bin/bash

VENV_DIR="sd-venv"

echo "====================================="
echo "Setting up environment"
echo "====================================="

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment"
source "$VENV_DIR/bin/activate"

echo ""
echo "Upgrading pip"
python -m pip install --upgrade pip

echo ""
echo "Installing PyTorch (MPS / CPU build)..."

# macOS does NOT use CUDA
# Apple Silicon uses MPS (Metal Performance Shaders)
pip install torch torchvision torchaudio

echo ""
echo "Installing other requirements..."
pip install -r requirements.txt

echo ""
echo "Starting app..."
python main.py