from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


# ──────────────────── Machine ────────────────────
class MachineBase(BaseModel):
    name: str
    machine_type: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None

class MachineCreate(MachineBase):
    pass

class MachineResponse(MachineBase):
    id: int
    class Config:
        from_attributes = True


# ──────────────────── Material ────────────────────
class MaterialBase(BaseModel):
    name: str
    material_type: str
    melt_temp_min: Optional[float] = None
    melt_temp_max: Optional[float] = None
    recommended_screw_speed_min: Optional[float] = None
    recommended_screw_speed_max: Optional[float] = None
    max_regrind_percentage: Optional[float] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    class Config:
        from_attributes = True


# ──────────────────── Solution ────────────────────
class SolutionBase(BaseModel):
    step_order: int
    description: str
    details: Optional[str] = None

class SolutionCreate(SolutionBase):
    pass

class SolutionResponse(SolutionBase):
    id: int
    problem_id: int
    source: str = "expert"

    class Config:
        from_attributes = True


# ──────────────────── Problem ────────────────────
class ProblemBase(BaseModel):
    problem_name: str
    process_type: str
    description: str
    severity: str = "medium"
    defect_category: Optional[str] = None
    machine_parameters: Optional[Dict[str, Any]] = None

class ProblemCreate(ProblemBase):
    pass

class ProblemResponse(ProblemBase):
    id: int
    solutions: List[SolutionResponse] = []

    class Config:
        from_attributes = True


# ──────────────────── Analysis Request ────────────────────
class MachineParameters(BaseModel):
    """All 9 machine parameters for analysis."""
    melt_temperature: Optional[float] = None
    extrusion_pressure: Optional[float] = None
    screw_speed: Optional[float] = None
    die_temperature: Optional[float] = None
    mold_temperature: Optional[float] = None
    cooling_time: Optional[float] = None
    cycle_time: Optional[float] = None
    material_type: Optional[str] = None
    regrind_percentage: Optional[float] = None

class AnalysisRequest(BaseModel):
    machine_parameters: Dict[str, Any]
    process_type: str

class AnalysisResponse(BaseModel):
    problem: Optional[ProblemResponse] = None
    ai_suggestion: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    fallback_used: bool = False


# ──────────────────── Defect Photo ────────────────────
class DefectDetection(BaseModel):
    defect_name: str
    confidence: Optional[float] = None

class DefectPhotoResponse(BaseModel):
    detected_defects: List[DefectDetection]
    matched_problems: List[ProblemResponse] = []
    ai_raw_response: Optional[str] = None


# ──────────────────── User Case (Learning) ────────────────────
class UserCaseBase(BaseModel):
    problem_id: int
    machine_parameters: Dict[str, Any]
    applied_solution_id: Optional[int] = None
    custom_solution_description: Optional[str] = None
    is_resolved: bool
    confidence_score: Optional[float] = None
    notes: Optional[str] = None

class UserCaseCreate(UserCaseBase):
    pass

class UserCaseResponse(UserCaseBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────── Troubleshooting Session ────────────────────
class StartSessionRequest(BaseModel):
    problem_id: int
    machine_parameters: Optional[Dict[str, Any]] = None

class StepFeedbackRequest(BaseModel):
    session_id: int
    solved: bool
    notes: Optional[str] = None
    custom_solution: Optional[str] = None  # If user solved with a different method

class SessionStepResponse(BaseModel):
    session_id: int
    problem_name: str
    current_step_order: int
    total_steps: int
    current_step: Optional[SolutionResponse] = None
    status: str  # in_progress / resolved / escalated
    message: str

class TroubleshootingSessionResponse(BaseModel):
    id: int
    problem_id: int
    current_step_order: int
    status: str
    machine_parameters: Optional[Dict[str, Any]] = None
    resolved_at_step: Optional[int] = None
    custom_resolution: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
