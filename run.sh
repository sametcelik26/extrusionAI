#!/bin/bash
echo "========================================="
echo "Starting ExtrusionAI Backend"
echo "========================================="

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

echo ""
echo "Checking Ollama AI Server..."
python check_ollama.py

echo ""
echo "Starting FastAPI Server..."
PORT=${1:-8000}

echo ""
echo "The database will be automatically created and seeded if it doesn't exist."
echo "API will be available at: http://127.0.0.1:$PORT"
echo "Swagger docs at:        http://127.0.0.1:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server."
echo "========================================="

uvicorn main:app --reload --port $PORT
