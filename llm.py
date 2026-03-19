import httpx
from typing import Dict, Any, List, Optional
import json
import re

OLLAMA_BASE_URL = "http://localhost:11434/api"


async def _get_first_available_model() -> str:
    """Check Ollama API and get the first available model (e.g., gemma3:4b)."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/tags", timeout=3.0)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    return models[0]["name"]
    except Exception:
        pass
    return ""


async def _is_ollama_available() -> bool:
    """Check if Ollama is running and has at least one model."""
    model = await _get_first_available_model()
    return bool(model)


async def generate_response(prompt: str, images: Optional[List[str]] = None) -> str:
    """Send text query to the first available Ollama model."""
    model = await _get_first_available_model()
    if not model:
        return "OLLAMA_ERROR: No models available."

    async with httpx.AsyncClient() as client:
        try:
            payload: Dict[str, Any] = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            if images:
                payload["images"] = images

            response = await client.post(
                f"{OLLAMA_BASE_URL}/generate",
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except httpx.RequestError as e:
            return f"OLLAMA_ERROR: {e}"
        except httpx.HTTPStatusError as e:
            return f"OLLAMA_ERROR: {e}"


async def analyze_problem_with_llm(parameters: Dict[str, Any], process_type: str, image_base64: Optional[str] = None) -> Dict[str, Any]:
    """
    Ask LLM to suggest the most probable problem using a strict JSON format.
    Falls back to a simple dict with error info if Ollama is offline.
    """
    model = await _get_first_available_model()
    if not model:
        return {
            "problem_name": "",
            "confidence": 0.0,
            "reasoning": "Ollama is not available. Using database fallback.",
            "ollama_available": False
        }

    # Include process type correctly: extrusion, injection, or blow molding
    image_prompt_addition = " and the attached defect image" if image_base64 else ""
    prompt = f"""You are an expert plastic manufacturing troubleshooter specializing in {process_type}.
It is crucial that your analysis works across extrusion, injection, and blow molding processes.

Analyze the following machine parameters (e.g., temperature, pressure, speed){image_prompt_addition} and identify the most probable production problem.

Machine Parameters:
{json.dumps(parameters, indent=2)}

Respond with this EXACT JSON format (no extra text around it):
{{
  "solution": "<short descriptive problem name or solution approach>",
  "notes": "<detailed explanation of why these parameters indicate this problem>",
  "recommended_params": {{
    "temperature": "<suggested range or value>",
    "pressure": "<suggested range or value>",
    "speed": "<suggested range or value>",
    "other": "<any other process-specific parameters>"
  }}
}}
"""

    raw = await generate_response(prompt, images=[image_base64] if image_base64 else None)

    if raw.startswith("OLLAMA_ERROR"):
        return {
            "problem_name": "",
            "confidence": 0.0,
            "reasoning": raw,
            "ollama_available": False
        }

    # Try to parse exact JSON from the response
    try:
        json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            # Map strict JSON onto the internal format for main.py compatibility, 
            # while preserving raw JSON logic so it's transparently passed.
            return {
                "problem_name": parsed.get("solution", ""),
                "confidence": 0.9,
                "reasoning": json.dumps(parsed, indent=2), # Store the whole JSON in reasoning
                "ollama_available": True
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback to mapping the raw, unparseable LLM output
    return {
        "problem_name": "Suggested Process Adjustment",
        "confidence": 0.5,
        "reasoning": raw,
        "ollama_available": True
    }


async def detect_defect_from_image(image_base64: str) -> Dict[str, Any]:
    """
    Send base64 encoded image to vision model.
    Returns dict: { defects: [{ name, confidence }], raw_response }
    """
    model = await _get_first_available_model()
    if not model:
        return {
            "defects": [],
            "raw_response": "Ollama is not available. Cannot analyze image.",
            "ollama_available": False
        }

    prompt = """Analyze this image of a manufactured plastic part. 
Identify ALL visible defects from this list:
- flash
- bubbles  
- streaks
- uneven_wall_thickness
- burn_marks
- melt_fracture
- warpage

Respond in this EXACT JSON format (no extra text):
{
  "defects": [
    {"name": "<defect_name>", "confidence": 0.0 to 1.0}
  ]
}

If no defects are visible, return: {"defects": []}"""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/generate",
                json={
                    "model": model,  # Rely on dynamic model
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            raw = data.get("response", "").strip()

            try:
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    defects = parsed.get("defects", [])
                    return {
                        "defects": defects,
                        "raw_response": raw,
                        "ollama_available": True
                    }
            except (json.JSONDecodeError, ValueError):
                pass

            known_defects = ["flash", "bubbles", "streaks", "uneven_wall_thickness",
                             "burn_marks", "melt_fracture", "warpage"]
            found = []
            raw_lower = raw.lower().replace(" ", "_").replace("-", "_")
            for d in known_defects:
                if d in raw_lower:
                    found.append({"name": d, "confidence": 0.5})

            return {
                "defects": found if found else [{"name": "unknown", "confidence": 0.3}],
                "raw_response": raw,
                "ollama_available": True
            }

        except httpx.RequestError as e:
            return {
                "defects": [],
                "raw_response": f"Error: {e}",
                "ollama_available": False
            }
        except httpx.HTTPStatusError as e:
            return {
                "defects": [],
                "raw_response": f"Error: {e}",
                "ollama_available": False
            }


async def suggest_next_step(problem_description: str, failed_steps: List[str],
                            machine_parameters: Dict[str, Any]) -> str:
    """Given previous failed steps, suggest what to try next."""
    if not await _is_ollama_available():
        return "Ollama is not available. Please follow the remaining steps in order."

    prompt = f"""You are an expert plastic manufacturing troubleshooter.

Problem: {problem_description}

Steps already tried (did NOT solve the problem):
{chr(10).join(f'- {s}' for s in failed_steps) if failed_steps else '- None yet'}

Current machine parameters:
{json.dumps(machine_parameters, indent=2) if machine_parameters else 'Not provided'}

Suggest ONE specific next troubleshooting action. Be concise and technical.
Respond with just the action description, nothing else."""

    raw = await generate_response(prompt)
    if raw.startswith("OLLAMA_ERROR"):
        return "Could not get AI suggestion. Please follow the remaining steps in order."
    return raw


async def analyze_parameters_against_standards(
    parameters: Dict[str, Any],
    material_type: Optional[str] = None,
    process_type: Optional[str] = None
) -> str:
    """Compare parameters to known good ranges and flag anomalies."""
    if not await _is_ollama_available():
        return "Ollama is not available. Cannot perform parameter analysis."

    prompt = f"""You are an expert in plastic manufacturing process optimization.

Analyze these machine parameters and identify any values that are outside normal operating ranges:

Process Type: {process_type or 'not specified'}
Material: {material_type or 'not specified'}
Parameters:
{json.dumps(parameters, indent=2)}

For each parameter, state if it's:
- NORMAL: within expected range
- WARNING: slightly outside range  
- CRITICAL: significantly outside range

Be concise and technical. Format as a bullet list."""

    raw = await generate_response(prompt)
    if raw.startswith("OLLAMA_ERROR"):
        return "Parameter analysis unavailable. Ollama is offline."
    return raw
