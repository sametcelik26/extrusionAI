# ExtrusionAI — Backend

ExtrusionAI is an intelligent troubleshooting assistant for plastic processing factories (Extrusion, Injection Molding, Blow Molding). It uses a local LLM (Ollama) to analyze production parameters and defect photos to provide step-by-step solutions.

## Prerequisites

- **Python 3.9+**
- **Ollama** (for local AI features)

## Setup & Run Instructions

This project includes automated scripts for quick setup and running.

### Windows

1. **Setup the environment (one-time):**
   Double-click `setup.bat` or run in terminal:
   ```cmd
   setup.bat
   ```

2. **Start the local AI (optional but recommended):**
   Make sure Ollama is installed and running, then pull the required models:
   ```cmd
   ollama run llama3
   ollama run llava
   ```

3. **Start the backend server:**
   Double-click `run.bat` or run in terminal:
   ```cmd
   run.bat
   ```
   *(To use a custom port, run: `run.bat 8080`)*

### Linux / Mac

1. **Setup the environment (one-time):**
   ```bash
   chmod +x setup.sh run.sh
   ./setup.sh
   ```

2. **Start the local AI (optional but recommended):**
   Make sure Ollama is installed and running, then pull the required models:
   ```bash
   ollama run llama3
   ollama run llava
   ```

3. **Start the backend server:**
   ```bash
   ./run.sh
   ```
   *(To use a custom port, run: `./run.sh 8080`)*

## Features

- **Automatic Database Setup:** On the first run, the SQLite database (`extrusion_ai.db`) is automatically created and seeded with sample machines, materials, and 16 common manufacturing problems with expert solutions.
- **Ollama Check:** The start script automatically checks if Ollama is running on port 11434 and warns you if it's missing. (The system uses an offline database fallback if Ollama is unavailable).
- **Health Check:** Test the system status anytime at `GET /health` (`http://localhost:8000/health`).

## API Documentation

Once the server is running, you can view and test all endpoints interactively via the Swagger UI:

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
