"""
Budget Service with AI-powered Insights
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.services.ai_service import AIService

class BudgetService:
    def __init__(self):
        self.ai_service = AIService()
    
    def get_transactions(
        self, 
        db: Session, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions for a user"""
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        return query.order_by(Transaction.date.desc()).limit(limit).all()
    
    async def get_budget_insights(
        self, 
        db: Session, 
        user_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """Get AI-powered budget insights"""
        # Get date range
        if month and year:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:
            # Current month
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1)
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1)
            else:
                end_date = datetime(now.year, now.month + 1, 1)
        
        transactions = self.get_transactions(db, user_id, start_date, end_date)
        
        # Convert to dict for AI analysis
        transactions_data = [
            {
                "amount": t.amount,
                "type": t.transaction_type.value,
                "category": t.category.value,
                "description": t.description,
                "date": t.date.isoformat()
            }
            for t in transactions
        ]
        
        # Get AI analysis
        ai_analysis = await self.ai_service.analyze_spending(transactions_data)
        
        # Calculate summary statistics
        total_income = sum(
            t.amount for t in transactions 
            if t.transaction_type == TransactionType.INCOME
        )
        total_expenses = sum(
            t.amount for t in transactions 
            if t.transaction_type == TransactionType.EXPENSE
        )
        
        # Category breakdown
        category_breakdown = {}
        for t in transactions:
            if t.transaction_type == TransactionType.EXPENSE:
                category_breakdown[t.category.value] = (
                    category_breakdown.get(t.category.value, 0) + t.amount
                )
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "net": total_income - total_expenses
            },
            "category_breakdown": category_breakdown,
            "ai_insights": ai_analysis
        }
    
    def get_category_spending(
        self, 
        db: Session, 
        user_id: int,
        category: TransactionCategory,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> float:
        """Get total spending for a category"""
        query = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.category == category,
                Transaction.transaction_type == TransactionType.EXPENSE
            )
        )
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        result = query.scalar()
        return result or 0.0

