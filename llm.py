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


async def analyze_problem_with_llm(parameters: Dict[str, Any], process_type: str, past_data: str, image_base64: Optional[str] = None) -> Dict[str, Any]:
    """
    Ask LLM to suggest the most probable problem.
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

    material_type = parameters.get("material_type", "Unknown")
    image_prompt_addition = "\nDefect Image Attached." if image_base64 else ""
    prompt = f"""You are a Senior Polymer Process Engineer AI integrated into the ExtrusionAI system.

Your objective is to provide a professional, industrial-grade diagnostic analysis.

You MUST follow these rules:
- Be material-aware. Current Material is: {material_type} (Remember material specific behaviors: HDPE high shrinkage risk, LDPE sagging tendency, PP sensitive to cooling, PVC extremely heat-sensitive/burn risk, PET moisture-critical, ABS/PC surface quality critical).
- Be process-aware. Current Process is: {process_type} (Extrusion, Injection, or Extrusion Blow Molding).
- Recognize defect patterns intelligently and expand your known defect database.
- Utilize a Parameter Correlation Engine: Analyze parameter combinations, not single variables (e.g., High temp + high screw speed -> Melt fracture; Low mold temp + fast cooling -> Warpage; High moisture + high regrind -> Bubbles).
- Provide prioritized solutions like an industrial troubleshooting PDF: Sequential, most probable -> least probable, fastest -> slowest, lowest cost -> highest cost.
- Do NOT provide generic answers. Be technical and actionable. Ensure real factory usability.

PAST SOLVED PROBLEMS & KNOWLEDGE DATABASE:
{past_data}

CURRENT MACHINE PARAMETERS & INPUT:
{json.dumps(parameters, indent=2)}{image_prompt_addition}

OUTPUT FORMAT (MANDATORY):
Every response must strictly follow this structure:

## Problem Name: <Specific Defect or Issue>

### 1. CLASSIFICATION
- **Process:** {process_type}
- **Material:** {material_type}
- **Defect Type:** <Choose from: Surface defects, Dimensional defects, Mechanical defects, Flow-related defects, Thermal degradation defects>

### 2. ROOT CAUSE GROUPING (CRITICAL)
<Organize all likely causes into these 5 main categories. Only include the relevant causes for this problem:>
1. **Material Issues** (e.g., Moisture, MFI mismatch, Contamination, Regrind ratio, Thermal sensitivity)
2. **Process Parameters** (e.g., Temperature profile, Screw speed, Back pressure, Pressure, Cooling time)
3. **Machine Issues** (e.g., Screw wear, Non-return valve leakage, Heater band failure, Accumulator issues)
4. **Tooling / Mold / Die** (e.g., Die misalignment, Gate design, Venting, Mold temperature imbalance)
5. **Operator / Environment** (e.g., Ambient humidity, Setup inconsistency, Insufficient purging)

### 3. STEP-BY-STEP SOLUTION SYSTEM
<Provide solutions sequentially starting from most probable/fastest/cheapest>
<Format each step EXACTLY like this:>
**Step [X]:**
- **Action:** <Specific technical action, e.g., Reduce melt temperature by 5-10°C>
- **Reason:** <Technical justification, e.g., Prevent polymer degradation>
- **Expected Result:** <What the operator will observe, e.g., Surface defects decrease>

### 4. PARAMETER RECOMMENDATIONS
<Provide optimized, specific parameter adjustments combining variables>

### 5. FOLLOW-UP
Did this solve the problem?
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
        "problem_name": "AI Analysis Complete",
        "confidence": 0.8,
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
