"""
Alert Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alert import AlertType, AlertPriority

class AlertCreate(BaseModel):
    alert_type: AlertType
    title: str
    message: str
    priority: AlertPriority = AlertPriority.MEDIUM
    alert_metadata: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    user_id: int
    alert_type: AlertType
    title: str
    message: str
    priority: AlertPriority
    is_read: bool
    alert_metadata: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

