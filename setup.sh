#!/bin/bash
echo "========================================="
echo "ExtrusionAI Setup (Linux/Mac)"
echo "========================================="

echo ""
echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 could not be found."
    echo "Please install Python 3.9+ to continue."
    exit 1
fi

echo ""
echo "[2/3] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo ""
echo "[3/3] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================="
echo "SETUP COMPLETE!"
echo "========================================="
echo "Next steps:"
echo "1. Ensure Ollama is installed (https://ollama.ai/)"
echo "2. Run: ./run.sh"
echo "========================================="
