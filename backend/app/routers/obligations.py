"""
Obligations Router for recurring payments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.obligation import ObligationCreate, ObligationResponse
from app.services.obligation_service import ObligationService
from app.core.security import get_current_user

router = APIRouter()
obligation_service = ObligationService()


@router.post("", response_model=ObligationResponse, status_code=status.HTTP_201_CREATED)
async def create_obligation(
    obligation: ObligationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obligation_service.create_obligation(db, current_user.id, obligation)


@router.get("", response_model=List[ObligationResponse])
async def list_obligations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return obligation_service.list_obligations(db, current_user.id)


@router.delete("/{obligation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_obligation(
    obligation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = obligation_service.delete_obligation(db, current_user.id, obligation_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation not found")

