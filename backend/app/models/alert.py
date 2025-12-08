"""
Alert Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class AlertType(str, enum.Enum):
    LOW_BALANCE = "low_balance"
    MISSED_SIP = "missed_sip"
    GOAL_DEADLINE = "goal_deadline"
    BUDGET_EXCEEDED = "budget_exceeded"
    OPPORTUNITY = "opportunity"
    RISK_WARNING = "risk_warning"
    DUE_SOON = "due_soon"
    PAST_DUE = "past_due"
    AUTO_PAY_FAIL = "auto_pay_fail"

class AlertPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    priority = Column(Enum(AlertPriority), default=AlertPriority.MEDIUM)
    is_read = Column(Boolean, default=False)
    alert_metadata = Column(String, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")

