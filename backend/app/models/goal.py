"""
Goal Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class GoalType(str, enum.Enum):
    RETIREMENT = "retirement"
    HOUSE = "house"
    EDUCATION = "education"
    VACATION = "vacation"
    EMERGENCY = "emergency"
    OTHER = "other"

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    goal_type = Column(Enum(GoalType), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime(timezone=True), nullable=False)
    monthly_contribution = Column(Float, nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    ai_plan = Column(String, nullable=True)  # JSON string with AI-generated plan
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")

