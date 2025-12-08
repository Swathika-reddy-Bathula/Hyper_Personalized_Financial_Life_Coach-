"""
Goal Service with AI Integration
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.goal import Goal, GoalStatus
from app.schemas.goal import GoalCreate, GoalUpdate
from app.services.ai_service import AIService

class GoalService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def create_goal(
        self, 
        db: Session, 
        goal: GoalCreate, 
        user_id: int,
        user_context: dict
    ) -> Goal:
        """Create a goal with AI-generated plan"""
        db_goal = Goal(**goal.model_dump(), user_id=user_id)
        
        # Generate AI plan
        ai_plan_data = await self.ai_service.understand_goal(
            goal.description or goal.title,
            user_context
        )
        db_goal.ai_plan = str(ai_plan_data)
        
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal
    
    def get_goals(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Goal]:
        """Get all goals for a user"""
        return db.query(Goal).filter(Goal.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_goal(self, db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
        """Get a specific goal"""
        return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    
    async def update_goal(
        self, 
        db: Session, 
        goal_id: int, 
        user_id: int, 
        goal_update: GoalUpdate
    ) -> Optional[Goal]:
        """Update a goal"""
        db_goal = self.get_goal(db, goal_id, user_id)
        if not db_goal:
            return None
        
        update_data = goal_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_goal, field, value)
        
        db.commit()
        db.refresh(db_goal)
        return db_goal
    
    def delete_goal(self, db: Session, goal_id: int, user_id: int) -> bool:
        """Delete a goal"""
        db_goal = self.get_goal(db, goal_id, user_id)
        if not db_goal:
            return False
        
        db.delete(db_goal)
        db.commit()
        return True

