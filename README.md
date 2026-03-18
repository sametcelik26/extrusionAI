# ExtrusionAI - Antigravity Project

**ExtrusionAI** is a manufacturing troubleshooting assistant designed for plastic processing factories.  
It helps operators solve production problems in **extrusion, injection molding, and blow molding** processes using AI-driven analysis and step-by-step solutions.

---

## Features

- **Problem Troubleshooting System**  
  - Predefined problems with ordered solution steps.  
  - Example: *Uneven Wall Thickness* → Check die mandrel centering → Adjust extrusion rate → …

- **Machine Parameter Analysis**  
  - Accepts parameters like melt temperature, pressure, screw speed, mold temperature, cooling time, material type, etc.  
  - Suggests the most probable problem based on inputs.

- **Photo Defect Detection**  
  - Upload a photo of the produced part.  
  - AI classifies defects such as flash, bubbles, streaks, uneven wall thickness, burn marks, melt fracture, warpage.

- **Interactive Troubleshooting Flow**  
  - Step-by-step solutions with user confirmation.  
  - Learning system updates database when alternative solutions are applied.

- **Learning System**  
  - Stores new solution paths with machine parameters and user-applied solutions.

---

## Technology Stack

- **Backend:** Python + FastAPI  
- **Database:** SQLite  
- **AI Integration:** Ollama AI (local model)  
- **Middleware:** Antigravity  
- **Frontend:** Planned integration with Lovable (web & mobile responsive)

---

## API Endpoints

- `/analyze_problem` – Analyze machine parameters and suggest probable problem  
- `/upload_defect_photo` – Classify defects from uploaded photo  
- `/get_troubleshooting_steps` – Return ordered solution steps  
- `/save_solution_case` – Store user-applied solution  
- `/get_similar_problems` – Retrieve similar problems from the database  

---

## Setup & Run

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/extrusionAI-antigravity.git
