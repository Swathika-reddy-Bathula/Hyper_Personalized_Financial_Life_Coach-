"""
Obligation Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.obligation import ObligationType, ObligationFrequency, ObligationStatus


class ObligationCreate(BaseModel):
    title: str
    obligation_type: ObligationType
    amount: float
    provider: Optional[str] = None
    due_date: datetime
    next_due_date: Optional[datetime] = None
    frequency: ObligationFrequency = ObligationFrequency.MONTHLY
    autopay_enabled: bool = False
    status: ObligationStatus = ObligationStatus.ACTIVE
    metadata: Optional[str] = None


class ObligationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    obligation_type: ObligationType
    amount: float
    provider: Optional[str] = None
    due_date: datetime
    next_due_date: Optional[datetime] = None
    frequency: ObligationFrequency
    autopay_enabled: bool
    status: ObligationStatus
    metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

