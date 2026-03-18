from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    machine_type = Column(String)  # extrusion / injection / blow_molding
    manufacturer = Column(String, nullable=True)
    model_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    material_type = Column(String)  # PE, PP, PVC, PS, ABS, PET, PA, PC, etc.
    melt_temp_min = Column(Float, nullable=True)
    melt_temp_max = Column(Float, nullable=True)
    recommended_screw_speed_min = Column(Float, nullable=True)
    recommended_screw_speed_max = Column(Float, nullable=True)
    max_regrind_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_name = Column(String, index=True)
    process_type = Column(String, index=True)  # extrusion / injection / blow_molding
    description = Column(Text)
    severity = Column(String, default="medium")  # low / medium / high / critical
    defect_category = Column(String, nullable=True, index=True)  # flash, bubbles, streaks, etc.
    machine_parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    solutions = relationship("Solution", back_populates="problem", order_by="Solution.step_order")


class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    step_order = Column(Integer)
    description = Column(Text)
    details = Column(Text, nullable=True)  # Extended explanation
    source = Column(String, default="expert")  # expert / user_learned

    problem = relationship("Problem", back_populates="solutions")


class UserCase(Base):
    __tablename__ = "user_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    machine_parameters = Column(JSON)
    applied_solution_id = Column(Integer, ForeignKey("solutions.id"), nullable=True)
    custom_solution_description = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    problem = relationship("Problem")
    applied_solution = relationship("Solution")


class TroubleshootingSession(Base):
    __tablename__ = "troubleshooting_sessions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    current_step_order = Column(Integer, default=1)
    status = Column(String, default="in_progress")  # in_progress / resolved / escalated
    machine_parameters = Column(JSON, nullable=True)
    resolved_at_step = Column(Integer, nullable=True)
    custom_resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    problem = relationship("Problem")
