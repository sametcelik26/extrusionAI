@echo off
echo =========================================
echo Starting ExtrusionAI Backend
echo =========================================

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Checking Ollama AI Server...
python check_ollama.py

echo.
echo Starting FastAPI Server...
set PORT=8000
if not "%~1"=="" set PORT=%~1

echo.
echo The database will be automatically created and seeded if it doesn't exist.
echo API will be available at: http://127.0.0.1:%PORT%
echo Swagger docs at:        http://127.0.0.1:%PORT%/docs
echo.
echo Press Ctrl+C to stop the server.
echo =========================================

uvicorn main:app --reload --port %PORT%
