"""
Goal Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.goal import GoalStatus, GoalType

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    goal_type: GoalType
    target_amount: float
    target_date: datetime
    monthly_contribution: Optional[float] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    monthly_contribution: Optional[float] = None
    status: Optional[GoalStatus] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    current_amount: float
    status: GoalStatus
    ai_plan: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

