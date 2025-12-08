"""
Alert Service for Predictive Financial Alerts
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from app.models.alert import Alert, AlertType, AlertPriority
from app.models.goal import Goal
from app.models.obligation import Obligation, ObligationStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import User

class AlertService:
    def check_low_balance(self, db: Session, user_id: int, threshold: float = 10000) -> Optional[Alert]:
        """Check for low account balance"""
        # Calculate current balance from transactions
        total_income = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.INCOME
            )
        ).scalar() or 0
        
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.EXPENSE
            )
        ).scalar() or 0
        
        balance = total_income - total_expenses
        
        if balance < threshold:
            # Check if alert already exists
            existing = db.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.alert_type == AlertType.LOW_BALANCE,
                    Alert.is_read == False
                )
            ).first()
            
            if not existing:
                alert = Alert(
                    user_id=user_id,
                    alert_type=AlertType.LOW_BALANCE,
                    title="Low Account Balance",
                    message=f"Your account balance ({balance:.2f}) is below the recommended threshold ({threshold}).",
                    priority=AlertPriority.HIGH,
                    alert_metadata=f'{{"balance": {balance}, "threshold": {threshold}}}'
                )
                db.add(alert)
                db.commit()
                return alert
        
        return None
    
    def check_goal_deadlines(self, db: Session, user_id: int) -> List[Alert]:
        """Check for approaching goal deadlines"""
        alerts = []
        thirty_days_from_now = datetime.now() + timedelta(days=30)
        
        goals = db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.status == "active",
                Goal.target_date <= thirty_days_from_now,
                Goal.target_date >= datetime.now()
            )
        ).all()
        
        for goal in goals:
            # Check if alert already exists
            existing = db.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.alert_type == AlertType.GOAL_DEADLINE,
                    Alert.alert_metadata.contains(f'"goal_id": {goal.id}'),
                    Alert.is_read == False
                )
            ).first()
            
            if not existing:
                days_remaining = (goal.target_date - datetime.now()).days
                progress = (goal.current_amount / goal.target_amount) * 100
                
                alert = Alert(
                    user_id=user_id,
                    alert_type=AlertType.GOAL_DEADLINE,
                    title=f"Goal Deadline Approaching: {goal.title}",
                    message=f"Your goal '{goal.title}' deadline is in {days_remaining} days. Current progress: {progress:.1f}%",
                    priority=AlertPriority.MEDIUM if progress > 50 else AlertPriority.HIGH,
                    alert_metadata=f'{{"goal_id": {goal.id}, "days_remaining": {days_remaining}, "progress": {progress}}}'
                )
                db.add(alert)
                alerts.append(alert)
        
        if alerts:
            db.commit()
        
        return alerts
    
    def check_budget_exceeded(
        self, 
        db: Session, 
        user_id: int, 
        category: Optional[str] = None
    ) -> Optional[Alert]:
        """Check if budget is exceeded for current month"""
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        # This is a simplified check - in production, you'd have budget limits per category
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.date >= start_of_month
            )
        ).scalar() or 0
        
        # Get user income to estimate budget
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.income:
            estimated_budget = user.income * 0.8  # Assume 80% of income as budget
            if total_expenses > estimated_budget:
                existing = db.query(Alert).filter(
                    and_(
                        Alert.user_id == user_id,
                        Alert.alert_type == AlertType.BUDGET_EXCEEDED,
                        Alert.is_read == False,
                        func.date(Alert.created_at) >= start_of_month.date()
                    )
                ).first()
                
                if not existing:
                    alert = Alert(
                        user_id=user_id,
                        alert_type=AlertType.BUDGET_EXCEEDED,
                        title="Monthly Budget Exceeded",
                        message=f"You have exceeded your estimated monthly budget. Expenses: {total_expenses:.2f}, Budget: {estimated_budget:.2f}",
                        priority=AlertPriority.HIGH,
                        alert_metadata=f'{{"expenses": {total_expenses}, "budget": {estimated_budget}}}'
                    )
                    db.add(alert)
                    db.commit()
                    return alert
        
        return None
    
    def get_alerts(
        self, 
        db: Session, 
        user_id: int, 
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[Alert]:
        """Get alerts for a user"""
        query = db.query(Alert).filter(Alert.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(Alert.is_read == is_read)
        
        return query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    def mark_alert_read(self, db: Session, alert_id: int, user_id: int) -> bool:
        """Mark an alert as read"""
        alert = db.query(Alert).filter(
            and_(Alert.id == alert_id, Alert.user_id == user_id)
        ).first()
        
        if alert:
            alert.is_read = True
            db.commit()
            return True
        return False

    def check_obligations_due(
        self,
        db: Session,
        user_id: int,
        days_before: int = 5
    ) -> List[Alert]:
        """Generate alerts for obligations that are due soon or past due."""
        now = datetime.now()
        soon = now + timedelta(days=days_before)
        alerts: List[Alert] = []

        obligations = db.query(Obligation).filter(
            and_(
                Obligation.user_id == user_id,
                Obligation.status == ObligationStatus.ACTIVE
            )
        ).all()

        for obligation in obligations:
            due_date = obligation.next_due_date or obligation.due_date
            if not due_date:
                continue

            is_past_due = due_date < now
            is_due_soon = now <= due_date <= soon

            if not (is_past_due or is_due_soon):
                continue

            existing = db.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.alert_type.in_([AlertType.DUE_SOON, AlertType.PAST_DUE]),
                    Alert.alert_metadata.contains(f'"obligation_id": {obligation.id}'),
                    Alert.is_read == False
                )
            ).first()

            if existing:
                continue

            alert_type = AlertType.PAST_DUE if is_past_due else AlertType.DUE_SOON
            days_delta = (due_date - now).days
            message = (
                f"{obligation.title} payment of {obligation.amount:.2f} is past due."
                if is_past_due
                else f"{obligation.title} payment of {obligation.amount:.2f} is due in {days_delta} days."
            )

            alert = Alert(
                user_id=user_id,
                alert_type=alert_type,
                title=f"Payment Reminder: {obligation.title}",
                message=message,
                priority=AlertPriority.HIGH if is_past_due else AlertPriority.MEDIUM,
                alert_metadata=f'{{"obligation_id": {obligation.id}, "due_date": "{due_date.isoformat()}"}}'
            )
            db.add(alert)
            alerts.append(alert)

        if alerts:
            db.commit()

        return alerts
    
    def generate_all_alerts(self, db: Session, user_id: int) -> List[Alert]:
        """Generate all predictive alerts for a user"""
        alerts = []
        
        # Check various alert conditions
        low_balance_alert = self.check_low_balance(db, user_id)
        if low_balance_alert:
            alerts.append(low_balance_alert)
        
        goal_alerts = self.check_goal_deadlines(db, user_id)
        alerts.extend(goal_alerts)

        obligation_alerts = self.check_obligations_due(db, user_id)
        alerts.extend(obligation_alerts)
        
        budget_alert = self.check_budget_exceeded(db, user_id)
        if budget_alert:
            alerts.append(budget_alert)
        
        return alerts

