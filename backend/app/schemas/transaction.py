"""
Transaction Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionCategory

class TransactionBase(BaseModel):
    amount: float
    transaction_type: TransactionType
    category: TransactionCategory
    description: Optional[str] = None
    merchant: Optional[str] = None
    date: datetime

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

