import asyncio
import json
from main import health_check, analyze_problem
from schemas import AnalysisRequest
from database import SessionLocal

async def test():
    db = SessionLocal()
    health = await health_check(db)
    print('Health:')
    print(json.dumps(health, indent=2))
    
    req = AnalysisRequest(machine_parameters={'melt_temperature': 'high'}, process_type='extrusion')
    analysis = await analyze_problem(req, db)
    print('Analysis:')
    print(analysis.model_dump_json(indent=2))
    
    db.close()

if __name__ == "__main__":
    asyncio.run(test())
