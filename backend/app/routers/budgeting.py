"""
Budgeting Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.budget_service import BudgetService
from app.core.security import get_current_user

router = APIRouter()
budget_service = BudgetService()

@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    from app.models.transaction import Transaction
    
    db_transaction = Transaction(**transaction.model_dump(), user_id=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/insights")
async def get_budget_insights(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered budget insights"""
    insights = await budget_service.get_budget_insights(
        db, current_user.id, month, year
    )
    return insights

@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions for the current user"""
    transactions = budget_service.get_transactions(
        db, current_user.id, limit=limit
    )
    return transactions

