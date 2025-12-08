"""
Alerts Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.services.alert_service import AlertService
from app.core.security import get_current_user

router = APIRouter()
alert_service = AlertService()

@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts for the current user"""
    alerts = alert_service.get_alerts(db, current_user.id, is_read, limit)
    return alerts

@router.post("/generate")
async def generate_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate all predictive alerts for the current user"""
    alerts = alert_service.generate_all_alerts(db, current_user.id)
    return {
        "message": f"Generated {len(alerts)} alerts",
        "alerts": [AlertResponse.model_validate(a).model_dump() for a in alerts]
    }

@router.post("/{alert_id}/read", status_code=200)
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as read"""
    success = alert_service.mark_alert_read(db, alert_id, current_user.id)
    return {"success": success}

