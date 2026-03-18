from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas
from typing import List, Optional
from datetime import datetime, timezone


# ──────────────────── Machine ────────────────────
def create_machine(db: Session, machine: schemas.MachineCreate) -> models.Machine:
    db_machine = models.Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

def get_machines(db: Session, skip: int = 0, limit: int = 100) -> List[models.Machine]:
    return db.query(models.Machine).offset(skip).limit(limit).all()

def get_machines_by_type(db: Session, machine_type: str) -> List[models.Machine]:
    return db.query(models.Machine).filter(models.Machine.machine_type == machine_type).all()


# ──────────────────── Material ────────────────────
def create_material(db: Session, material: schemas.MaterialCreate) -> models.Material:
    db_material = models.Material(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def get_materials(db: Session, skip: int = 0, limit: int = 100) -> List[models.Material]:
    return db.query(models.Material).offset(skip).limit(limit).all()

def get_material_by_type(db: Session, material_type: str) -> Optional[models.Material]:
    return db.query(models.Material).filter(models.Material.material_type == material_type).first()


# ──────────────────── Problem ────────────────────
def get_problem(db: Session, problem_id: int) -> Optional[models.Problem]:
    return db.query(models.Problem).filter(models.Problem.id == problem_id).first()

def get_problems(db: Session, skip: int = 0, limit: int = 100) -> List[models.Problem]:
    return db.query(models.Problem).offset(skip).limit(limit).all()

def get_problems_by_process(db: Session, process_type: str) -> List[models.Problem]:
    return db.query(models.Problem).filter(models.Problem.process_type == process_type).all()

def get_problems_by_defect_category(db: Session, defect_category: str) -> List[models.Problem]:
    return db.query(models.Problem).filter(
        models.Problem.defect_category == defect_category
    ).all()

def search_problems(db: Session, query: str) -> List[models.Problem]:
    """Text search across problem name and description."""
    pattern = f"%{query}%"
    return db.query(models.Problem).filter(
        or_(
            models.Problem.problem_name.ilike(pattern),
            models.Problem.description.ilike(pattern)
        )
    ).all()

def create_problem(db: Session, problem: schemas.ProblemCreate) -> models.Problem:
    db_problem = models.Problem(**problem.model_dump())
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem


# ──────────────────── Solution ────────────────────
def create_solution(db: Session, problem_id: int, solution: schemas.SolutionCreate) -> models.Solution:
    db_solution = models.Solution(**solution.model_dump(), problem_id=problem_id)
    db.add(db_solution)
    db.commit()
    db.refresh(db_solution)
    return db_solution

def get_solutions_by_problem(db: Session, problem_id: int) -> List[models.Solution]:
    return db.query(models.Solution).filter(
        models.Solution.problem_id == problem_id
    ).order_by(models.Solution.step_order).all()


# ──────────────────── User Case (Learning) ────────────────────
def create_user_case(db: Session, user_case: schemas.UserCaseCreate) -> models.UserCase:
    db_uc = models.UserCase(**user_case.model_dump())
    db.add(db_uc)
    db.commit()
    db.refresh(db_uc)
    return db_uc

def get_user_cases(db: Session, problem_id: Optional[int] = None,
                   skip: int = 0, limit: int = 50) -> List[models.UserCase]:
    query = db.query(models.UserCase)
    if problem_id:
        query = query.filter(models.UserCase.problem_id == problem_id)
    return query.order_by(models.UserCase.created_at.desc()).offset(skip).limit(limit).all()

def get_similar_user_cases(db: Session, problem_id: int) -> List[models.UserCase]:
    """Find past resolved cases for the same problem."""
    return db.query(models.UserCase).filter(
        models.UserCase.problem_id == problem_id,
        models.UserCase.is_resolved == True
    ).order_by(models.UserCase.created_at.desc()).limit(10).all()


# ──────────────────── Troubleshooting Session ────────────────────
def create_session(db: Session, problem_id: int,
                   machine_parameters: Optional[dict] = None) -> models.TroubleshootingSession:
    session = models.TroubleshootingSession(
        problem_id=problem_id,
        current_step_order=1,
        status="in_progress",
        machine_parameters=machine_parameters
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: Session, session_id: int) -> Optional[models.TroubleshootingSession]:
    return db.query(models.TroubleshootingSession).filter(
        models.TroubleshootingSession.id == session_id
    ).first()

def advance_session(db: Session, session_id: int) -> models.TroubleshootingSession:
    """Move session to next step."""
    session = get_session(db, session_id)
    if session:
        session.current_step_order += 1
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session

def resolve_session(db: Session, session_id: int, step_order: int,
                    custom_resolution: Optional[str] = None) -> models.TroubleshootingSession:
    """Mark session as resolved."""
    session = get_session(db, session_id)
    if session:
        session.status = "resolved"
        session.resolved_at_step = step_order
        session.custom_resolution = custom_resolution
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session

def escalate_session(db: Session, session_id: int) -> models.TroubleshootingSession:
    """Mark session as escalated (all steps exhausted, not resolved)."""
    session = get_session(db, session_id)
    if session:
        session.status = "escalated"
        session.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session
