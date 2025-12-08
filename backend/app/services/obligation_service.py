"""
Service for managing recurring financial obligations
"""
from sqlalchemy.orm import Session
from typing import List
from app.models.obligation import Obligation
from app.schemas.obligation import ObligationCreate


class ObligationService:
    def create_obligation(self, db: Session, user_id: int, payload: ObligationCreate) -> Obligation:
        obligation = Obligation(**payload.model_dump(), user_id=user_id)
        db.add(obligation)
        db.commit()
        db.refresh(obligation)
        return obligation

    def list_obligations(self, db: Session, user_id: int) -> List[Obligation]:
        return db.query(Obligation).filter(Obligation.user_id == user_id).order_by(Obligation.due_date.asc()).all()

    def delete_obligation(self, db: Session, user_id: int, obligation_id: int) -> bool:
        obligation = db.query(Obligation).filter(Obligation.user_id == user_id, Obligation.id == obligation_id).first()
        if not obligation:
            return False
        db.delete(obligation)
        db.commit()
        return True

