import json
import httpx
import asyncio
from typing import Dict, Any

from database import SessionLocal
import crud

OLLAMA_BASE_URL = "http://localhost:11434/api"

async def get_first_available_model() -> str:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/tags", timeout=3.0)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    return models[0]["name"]
    except Exception:
        pass
    return None

async def solve_problem() -> Dict[str, Any]:
    # Dummy parameters since none were provided
    dummy_params = {"melt_temperature": 210, "extrusion_pressure": 150}
    
    model = await get_first_available_model()
    
    if model:
        prompt = f"""You are ExtrusionAI's local assistant for the plastics industry.
A user has provided a defect photo (burn marks) and machine parameters: {json.dumps(dummy_params)}.
Generate a solution for this issue.
Always return the solution in exactly this JSON format:
{{
  "solution": "...",
  "notes": "...",
  "recommended_params": {{...}}
}}
Return ONLY valid JSON.
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    resp_json = response.json()
                    # Parse the string response which should be JSON
                    ai_reply = json.loads(resp_json.get("response", "{}"))
                    ai_reply["_meta"] = {"source": "ollama", "model_used": model}
                    return ai_reply
        except Exception as e:
            pass # Fallback to DB
            
    # Fallback to local DB
    db = SessionLocal()
    try:
        problems = crud.get_problems(db)
        if problems:
            # Pick the first one or a specific one for the fallback
            p = problems[0]
            solutions = crud.get_solutions_by_problem(db, p.id)
            sol_text = solutions[0].description if solutions else "Perform standard machine maintenance."
            return {
                "solution": f"Fallback to DB: {p.problem_name} - {sol_text}",
                "notes": f"Ollama is offline or no models found. Retrieved from local database. Description: {p.description}",
                "recommended_params": {"melt_temperature": "Check standard range", "extrusion_pressure": "Check standard range"},
                "_meta": {"source": "database_fallback", "model_used": None}
            }
        else:
            return {
                "solution": "No solution found. Database is empty.",
                "notes": "Ollama is offline and no local problems available.",
                "recommended_params": {},
                "_meta": {"source": "fallback", "model_used": None}
            }
    finally:
        db.close()

if __name__ == "__main__":
    result = asyncio.run(solve_problem())
    print(json.dumps(result, indent=2, ensure_ascii=False))
