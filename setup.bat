@echo off
echo =========================================
echo ExtrusionAI Setup (Windows)
echo =========================================

echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://www.python.org/
    exit /b 1
)

echo.
echo [2/3] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =========================================
echo SETUP COMPLETE!
echo =========================================
echo Next steps:
echo 1. Ensure Ollama is installed (https://ollama.ai/)
echo 2. Run: run.bat
echo =========================================
pause
