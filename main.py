from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import base64

import models, schemas, crud, ollama_client
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ExtrusionAI Backend",
    description="Intelligent troubleshooting assistant for plastic processing factories",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
#  Health Check
# ═══════════════════════════════════════════════════════════════
@app.get("/")
def read_root():
    return {"message": "ExtrusionAI API is running", "version": "2.0.0"}


# ═══════════════════════════════════════════════════════════════
#  Problem Analysis (AI-powered)
# ═══════════════════════════════════════════════════════════════
@app.post("/analyze_problem", response_model=schemas.AnalysisResponse)
async def analyze_problem(request: schemas.AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze machine parameters to identify the most probable production problem.
    Uses Ollama LLM when available, falls back to database matching.
    """
    # Try LLM analysis
    llm_result = await ollama_client.analyze_problem_with_llm(
        request.machine_parameters,
        request.process_type
    )

    ollama_available = llm_result.get("ollama_available", False)
    problem_name = llm_result.get("problem_name", "")
    confidence = llm_result.get("confidence", 0.0)
    reasoning = llm_result.get("reasoning", "")

    # Search database for matching problem
    problems = crud.get_problems_by_process(db, request.process_type)

    matched_problem = None
    if problem_name:
        # Try exact-ish match from LLM suggestion
        for p in problems:
            p_lower = p.problem_name.lower().replace("_", " ").replace("-", " ")
            llm_lower = problem_name.lower().replace("_", " ").replace("-", " ")
            if p_lower in llm_lower or llm_lower in p_lower:
                matched_problem = p
                break

        # Try partial word match
        if not matched_problem:
            llm_words = set(problem_name.lower().split())
            best_score = 0
            for p in problems:
                p_words = set(p.problem_name.lower().split())
                overlap = len(llm_words & p_words)
                if overlap > best_score:
                    best_score = overlap
                    matched_problem = p

    # DB fallback: parameter-based matching when no LLM or no match
    if not matched_problem and problems:
        # Return first problem of matching process type as basic fallback
        matched_problem = problems[0]
        if not ollama_available:
            reasoning = "Ollama offline — returning problems for the specified process type."
            confidence = 0.3

    return schemas.AnalysisResponse(
        problem=schemas.ProblemResponse.model_validate(matched_problem) if matched_problem else None,
        ai_suggestion=problem_name if problem_name else None,
        confidence=confidence,
        reasoning=reasoning,
        fallback_used=not ollama_available
    )


# ═══════════════════════════════════════════════════════════════
#  Defect Photo Detection (AI-powered)
# ═══════════════════════════════════════════════════════════════
@app.post("/upload_defect_photo", response_model=schemas.DefectPhotoResponse)
async def upload_defect_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a photo of a plastic part to classify defects.
    Returns detected defects with confidence and matched problems from the database.
    """
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")

    result = await ollama_client.detect_defect_from_image(image_base64)

    defects = result.get("defects", [])
    raw_response = result.get("raw_response", "")

    # Find matching problems for each detected defect
    matched_problems = []
    seen_ids = set()
    for defect in defects:
        defect_name = defect.get("name", "").lower().replace(" ", "_")
        db_problems = crud.get_problems_by_defect_category(db, defect_name)
        for p in db_problems:
            if p.id not in seen_ids:
                matched_problems.append(schemas.ProblemResponse.model_validate(p))
                seen_ids.add(p.id)

    return schemas.DefectPhotoResponse(
        detected_defects=[
            schemas.DefectDetection(
                defect_name=d.get("name", "unknown"),
                confidence=d.get("confidence")
            ) for d in defects
        ],
        matched_problems=matched_problems,
        ai_raw_response=raw_response
    )


# ═══════════════════════════════════════════════════════════════
#  Troubleshooting Steps
# ═══════════════════════════════════════════════════════════════
@app.get("/get_troubleshooting_steps/{problem_id}", response_model=List[schemas.SolutionResponse])
def get_troubleshooting_steps(problem_id: int, db: Session = Depends(get_db)):
    """Get ordered troubleshooting steps for a specific problem."""
    problem = crud.get_problem(db, problem_id=problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    solutions = crud.get_solutions_by_problem(db, problem_id=problem_id)
    return solutions


# ═══════════════════════════════════════════════════════════════
#  Save Solution Case (Learning System)
# ═══════════════════════════════════════════════════════════════
@app.post("/save_solution_case", response_model=schemas.UserCaseResponse)
def save_solution_case(user_case: schemas.UserCaseCreate, db: Session = Depends(get_db)):
    """
    Save a user's troubleshooting case. If a custom solution was used,
    the learning system automatically adds it as a new troubleshooting step.
    """
    db_case = crud.create_user_case(db, user_case)

    # Learning System: add custom solution as a new troubleshooting path
    if (user_case.is_resolved
            and user_case.custom_solution_description
            and not user_case.applied_solution_id):
        existing_solutions = crud.get_solutions_by_problem(db, user_case.problem_id)
        next_step = len(existing_solutions) + 1

        new_solution = schemas.SolutionCreate(
            step_order=next_step,
            description=user_case.custom_solution_description,
            details="Learned from user case"
        )
        crud.create_solution(db, user_case.problem_id, new_solution)

    return db_case


# ═══════════════════════════════════════════════════════════════
#  Similar Problems
# ═══════════════════════════════════════════════════════════════
@app.post("/get_similar_problems", response_model=List[schemas.ProblemResponse])
def get_similar_problems(request: schemas.AnalysisRequest, db: Session = Depends(get_db)):
    """Find similar problems by process type, with optional text search."""
    problems = crud.get_problems_by_process(db, request.process_type)
    return problems[:5]


# ═══════════════════════════════════════════════════════════════
#  Interactive Troubleshooting Flow
# ═══════════════════════════════════════════════════════════════
@app.post("/start_troubleshooting", response_model=schemas.SessionStepResponse)
def start_troubleshooting(request: schemas.StartSessionRequest, db: Session = Depends(get_db)):
    """
    Start an interactive troubleshooting session for a problem.
    Returns the first step to try.
    """
    problem = crud.get_problem(db, request.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    solutions = crud.get_solutions_by_problem(db, request.problem_id)
    if not solutions:
        raise HTTPException(status_code=404, detail="No troubleshooting steps found for this problem")

    session = crud.create_session(db, request.problem_id, request.machine_parameters)

    return schemas.SessionStepResponse(
        session_id=session.id,
        problem_name=problem.problem_name,
        current_step_order=1,
        total_steps=len(solutions),
        current_step=schemas.SolutionResponse.model_validate(solutions[0]),
        status="in_progress",
        message=f"Step 1 of {len(solutions)}: {solutions[0].description}"
    )


@app.post("/step_feedback", response_model=schemas.SessionStepResponse)
def step_feedback(feedback: schemas.StepFeedbackRequest, db: Session = Depends(get_db)):
    """
    Report the result of a troubleshooting step.
    If solved → save resolution and close session.
    If not solved → advance to next step or escalate.
    """
    session = crud.get_session(db, feedback.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail=f"Session is already {session.status}")

    problem = crud.get_problem(db, session.problem_id)
    solutions = crud.get_solutions_by_problem(db, session.problem_id)
    total_steps = len(solutions)

    if feedback.solved:
        # Problem resolved!
        custom_res = feedback.custom_solution if feedback.custom_solution else None
        session = crud.resolve_session(
            db, feedback.session_id, session.current_step_order, custom_res
        )

        # If solved with a custom method, add it to the knowledge base (Learning System)
        if feedback.custom_solution:
            next_step = total_steps + 1
            new_sol = schemas.SolutionCreate(
                step_order=next_step,
                description=feedback.custom_solution,
                details=f"Learned from troubleshooting session #{session.id}"
            )
            crud.create_solution(db, session.problem_id, new_sol)

        # Save as user case
        crud.create_user_case(db, schemas.UserCaseCreate(
            problem_id=session.problem_id,
            machine_parameters=session.machine_parameters or {},
            applied_solution_id=solutions[session.resolved_at_step - 1].id
                if session.resolved_at_step and session.resolved_at_step <= total_steps else None,
            custom_solution_description=custom_res,
            is_resolved=True,
            notes=feedback.notes
        ))

        return schemas.SessionStepResponse(
            session_id=session.id,
            problem_name=problem.problem_name,
            current_step_order=session.resolved_at_step or session.current_step_order,
            total_steps=total_steps,
            current_step=None,
            status="resolved",
            message=f"Problem resolved at step {session.resolved_at_step}! Solution saved."
        )
    else:
        # Not solved — advance to next step
        if session.current_step_order >= total_steps:
            # All steps exhausted
            session = crud.escalate_session(db, feedback.session_id)

            # Save unresolved case for analysis
            crud.create_user_case(db, schemas.UserCaseCreate(
                problem_id=session.problem_id,
                machine_parameters=session.machine_parameters or {},
                is_resolved=False,
                notes=feedback.notes
            ))

            return schemas.SessionStepResponse(
                session_id=session.id,
                problem_name=problem.problem_name,
                current_step_order=session.current_step_order,
                total_steps=total_steps,
                current_step=None,
                status="escalated",
                message="All troubleshooting steps exhausted. Consider contacting technical support or submitting a custom solution."
            )
        else:
            session = crud.advance_session(db, feedback.session_id)
            next_step_idx = session.current_step_order - 1
            next_solution = solutions[next_step_idx] if next_step_idx < len(solutions) else None

            return schemas.SessionStepResponse(
                session_id=session.id,
                problem_name=problem.problem_name,
                current_step_order=session.current_step_order,
                total_steps=total_steps,
                current_step=schemas.SolutionResponse.model_validate(next_solution) if next_solution else None,
                status="in_progress",
                message=f"Step {session.current_step_order} of {total_steps}: {next_solution.description if next_solution else 'N/A'}"
            )


@app.get("/session/{session_id}", response_model=schemas.TroubleshootingSessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get the current state of a troubleshooting session."""
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ═══════════════════════════════════════════════════════════════
#  Listings
# ═══════════════════════════════════════════════════════════════
@app.get("/problems", response_model=List[schemas.ProblemResponse])
def list_problems(
    process_type: Optional[str] = Query(None, description="Filter by process type"),
    defect_category: Optional[str] = Query(None, description="Filter by defect category"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    db: Session = Depends(get_db)
):
    """List all problems with optional filters."""
    if search:
        return crud.search_problems(db, search)
    if defect_category:
        return crud.get_problems_by_defect_category(db, defect_category)
    if process_type:
        return crud.get_problems_by_process(db, process_type)
    return crud.get_problems(db)


@app.get("/machines", response_model=List[schemas.MachineResponse])
def list_machines(db: Session = Depends(get_db)):
    """List all registered machines."""
    return crud.get_machines(db)


@app.get("/materials", response_model=List[schemas.MaterialResponse])
def list_materials(db: Session = Depends(get_db)):
    """List all registered materials."""
    return crud.get_materials(db)
