import httpx
import asyncio
from typing import Dict, Any
import json

API_URL = "http://localhost:8000"

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}{RESET}")


def print_result(label: str, status: int, data: dict):
    color = GREEN if 200 <= status < 300 else RED
    print(f"  {color}[{status}]{RESET} {label}")
    print(f"  {json.dumps(data, indent=2, default=str)[:500]}")
    print()


async def test_api():
    async with httpx.AsyncClient(timeout=30.0) as client:

        # ─── 1. Health Check ───
        print_header("1. Health Check — GET /")
        try:
            r = await client.get(f"{API_URL}/")
            print_result("Root endpoint", r.status_code, r.json())
        except Exception as e:
            print(f"  {RED}Connection failed: {e}{RESET}")
            print(f"  {YELLOW}Make sure the server is running: uvicorn main:app --reload{RESET}")
            return

        # ─── 2. List Problems ───
        print_header("2. List Problems — GET /problems")
        r = await client.get(f"{API_URL}/problems")
        problems = r.json()
        print_result(f"Found {len(problems)} problems", r.status_code, {"count": len(problems)})

        # Filter by process type
        r = await client.get(f"{API_URL}/problems", params={"process_type": "injection"})
        print_result("Filtered (injection)", r.status_code, {"count": len(r.json())})

        # Filter by defect category
        r = await client.get(f"{API_URL}/problems", params={"defect_category": "flash"})
        print_result("Filtered (flash)", r.status_code, {"count": len(r.json())})

        # Search
        r = await client.get(f"{API_URL}/problems", params={"search": "burn"})
        print_result("Search (burn)", r.status_code, {"count": len(r.json())})

        # ─── 3. List Machines ───
        print_header("3. List Machines — GET /machines")
        r = await client.get(f"{API_URL}/machines")
        print_result(f"Found {len(r.json())} machines", r.status_code, r.json()[:2])

        # ─── 4. List Materials ───
        print_header("4. List Materials — GET /materials")
        r = await client.get(f"{API_URL}/materials")
        print_result(f"Found {len(r.json())} materials", r.status_code, r.json()[:2])

        # ─── 5. Analyze Problem ───
        print_header("5. Analyze Problem — POST /analyze_problem")
        r = await client.post(
            f"{API_URL}/analyze_problem",
            json={
                "process_type": "extrusion",
                "machine_parameters": {
                    "melt_temperature": 250,
                    "extrusion_pressure": 200,
                    "die_temperature": 220,
                    "screw_speed": 80,
                    "material_type": "HDPE",
                    "regrind_percentage": 5
                }
            }
        )
        print_result("Analysis result", r.status_code, r.json())

        # ─── 6. Get Troubleshooting Steps ───
        print_header("6. Troubleshooting Steps — GET /get_troubleshooting_steps/1")
        r = await client.get(f"{API_URL}/get_troubleshooting_steps/1")
        print_result(f"Steps for problem #1", r.status_code, r.json())

        # ─── 7. Interactive Troubleshooting Flow ───
        print_header("7. Interactive Troubleshooting — POST /start_troubleshooting")

        # Start session
        r = await client.post(
            f"{API_URL}/start_troubleshooting",
            json={"problem_id": 1, "machine_parameters": {"melt_temperature": 210}}
        )
        session_data = r.json()
        session_id = session_data.get("session_id")
        print_result("Session started", r.status_code, session_data)

        if session_id:
            # Step 1: not solved
            print(f"  {YELLOW}→ Reporting Step 1 NOT solved...{RESET}")
            r = await client.post(
                f"{API_URL}/step_feedback",
                json={"session_id": session_id, "solved": False, "notes": "Did not fix it"}
            )
            print_result("Step feedback (not solved)", r.status_code, r.json())

            # Step 2: solved!
            print(f"  {YELLOW}→ Reporting Step 2 SOLVED!{RESET}")
            r = await client.post(
                f"{API_URL}/step_feedback",
                json={"session_id": session_id, "solved": True, "notes": "This fixed it"}
            )
            print_result("Step feedback (solved!)", r.status_code, r.json())

            # Check session state
            r = await client.get(f"{API_URL}/session/{session_id}")
            print_result("Session state", r.status_code, r.json())

        # ─── 8. Interactive Flow — Escalation ───
        print_header("8. Escalation Test — Exhaust All Steps")
        r = await client.post(
            f"{API_URL}/start_troubleshooting",
            json={"problem_id": 5}  # Streaks — 3 steps
        )
        esc_session = r.json()
        esc_id = esc_session.get("session_id")
        print_result("Session started (3-step problem)", r.status_code, esc_session)

        if esc_id:
            for i in range(3):
                r = await client.post(
                    f"{API_URL}/step_feedback",
                    json={"session_id": esc_id, "solved": False}
                )
            print_result("After exhausting all steps", r.status_code, r.json())

        # ─── 9. Save Solution Case (Learning System) ───
        print_header("9. Learning System — POST /save_solution_case")

        # Custom solution
        r = await client.post(
            f"{API_URL}/save_solution_case",
            json={
                "problem_id": 1,
                "machine_parameters": {"melt_temperature": 195, "screw_speed": 45},
                "is_resolved": True,
                "custom_solution_description": "Replaced the worn mandrel bushing and re-centered",
                "notes": "Bushing had 0.3mm wear"
            }
        )
        print_result("Custom solution saved", r.status_code, r.json())

        # Verify the new step was added
        r = await client.get(f"{API_URL}/get_troubleshooting_steps/1")
        steps = r.json()
        print_result(f"Steps for problem #1 AFTER learning (should have new step)", r.status_code,
                     {"step_count": len(steps), "last_step": steps[-1] if steps else None})

        # ─── 10. Similar Problems ───
        print_header("10. Similar Problems — POST /get_similar_problems")
        r = await client.post(
            f"{API_URL}/get_similar_problems",
            json={
                "process_type": "blow_molding",
                "machine_parameters": {}
            }
        )
        print_result(f"Similar (blow_molding)", r.status_code,
                     {"count": len(r.json()), "names": [p["problem_name"] for p in r.json()]})

        # ─── 11. Interactive Flow with Custom Solution ───
        print_header("11. Custom Solution via Session")
        r = await client.post(
            f"{API_URL}/start_troubleshooting",
            json={"problem_id": 6}  # Flash on injection
        )
        custom_session = r.json()
        custom_id = custom_session.get("session_id")

        if custom_id:
            # Solve with custom method
            r = await client.post(
                f"{API_URL}/step_feedback",
                json={
                    "session_id": custom_id,
                    "solved": True,
                    "custom_solution": "Applied mold release agent to parting surface"
                }
            )
            print_result("Solved with custom method", r.status_code, r.json())

            # Verify new step added to problem #6
            r = await client.get(f"{API_URL}/get_troubleshooting_steps/6")
            steps = r.json()
            print_result(f"Flash problem steps after learning", r.status_code,
                         {"step_count": len(steps), "last_step": steps[-1] if steps else None})

        # ─── Summary ───
        print_header("TEST SUMMARY")
        print(f"  {GREEN}All endpoint tests completed!{RESET}")
        print(f"  {YELLOW}Note: /analyze_problem and /upload_defect_photo use Ollama.")
        print(f"  If Ollama is not running, these endpoints use DB fallback.{RESET}")


if __name__ == "__main__":
    asyncio.run(test_api())
