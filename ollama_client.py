import httpx
from typing import Dict, Any, List, Optional
import json
import re

OLLAMA_BASE_URL = "http://localhost:11434/api"
DEFAULT_TEXT_MODEL = "llama3"
DEFAULT_VISION_MODEL = "llava"


async def _is_ollama_available() -> bool:
    """Check if Ollama is running."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://localhost:11434/", timeout=3.0)
            return resp.status_code == 200
    except Exception:
        return False


async def generate_response(prompt: str, model: str = DEFAULT_TEXT_MODEL) -> str:
    """Send text query to Ollama."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except httpx.RequestError as e:
            return f"OLLAMA_ERROR: {e}"
        except httpx.HTTPStatusError as e:
            return f"OLLAMA_ERROR: {e}"


async def analyze_problem_with_llm(parameters: Dict[str, Any], process_type: str) -> Dict[str, Any]:
    """
    Ask LLM to suggest the most probable problem.
    Returns structured dict: { problem_name, confidence, reasoning }
    Falls back to a simple dict with error info if Ollama is unavailable.
    """
    if not await _is_ollama_available():
        return {
            "problem_name": "",
            "confidence": 0.0,
            "reasoning": "Ollama is not available. Using database fallback.",
            "ollama_available": False
        }

    prompt = f"""You are an expert plastic manufacturing troubleshooter specializing in {process_type}.

Analyze the following machine parameters and identify the most probable production problem.

Machine Parameters:
{json.dumps(parameters, indent=2)}

Respond in this EXACT JSON format (no extra text):
{{
  "problem_name": "<short descriptive problem name>",
  "confidence": <0.0 to 1.0>,
  "reasoning": "<brief explanation of why these parameters indicate this problem>"
}}"""

    raw = await generate_response(prompt)

    if raw.startswith("OLLAMA_ERROR"):
        return {
            "problem_name": "",
            "confidence": 0.0,
            "reasoning": raw,
            "ollama_available": False
        }

    # Try to parse JSON from the response
    try:
        # Find JSON in the response (LLM might add extra text)
        json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {
                "problem_name": parsed.get("problem_name", ""),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reasoning": parsed.get("reasoning", ""),
                "ollama_available": True
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: treat entire response as the problem name
    return {
        "problem_name": raw[:200],
        "confidence": 0.5,
        "reasoning": "Could not parse structured response from LLM.",
        "ollama_available": True
    }


async def detect_defect_from_image(image_base64: str) -> Dict[str, Any]:
    """
    Send base64 encoded image to vision model.
    Returns dict: { defects: [{ name, confidence }], raw_response }
    """
    if not await _is_ollama_available():
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
    {"name": "<defect_name>", "confidence": <0.0 to 1.0>}
  ]
}

If no defects are visible, return: {"defects": []}"""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/generate",
                json={
                    "model": DEFAULT_VISION_MODEL,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            raw = data.get("response", "").strip()

            # Try to parse JSON
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

            # Fallback: try to extract defect names from text
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
