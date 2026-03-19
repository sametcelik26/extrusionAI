import asyncio
import json
from datetime import datetime
from main import health_check, analyze_problem
from schemas import AnalysisRequest
from database import SessionLocal

async def test():
    db = SessionLocal()
    
    # 3. Health Check
    health = await health_check(db)
    print('Health Response:')
    print(json.dumps(health, indent=2))
    
    # 4. Test Sample API Call
    payload = {
      "melt_temperature": 200,
      "extrusion_pressure": 50,
      "screw_speed": 100,
      "die_temperature": 210,
      "mold_temperature": 50,
      "cooling_time": 30,
      "cycle_time": 60,
      "material_type": "PVC",
      "regrind_percentage": 10
    }
    req = AnalysisRequest(machine_parameters=payload, process_type='extrusion')
    analysis = await analyze_problem(req, db)
    print('\nAnalysis Response:')
    print(analysis.model_dump_json(indent=2))
    
    # 5. Report Status
    report = {
        "database": health.get("database", "failed"),
        "ollama": "ready" if health.get("ollama") == "running" else "failed",
        "version": health.get("version", "2.0.0"),
        "last_checked": datetime.now().isoformat()
    }
    print('\nFinal Report:')
    print(json.dumps(report, indent=2))
    
    db.close()

if __name__ == "__main__":
    asyncio.run(test())
