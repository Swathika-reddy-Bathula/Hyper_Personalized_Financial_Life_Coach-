"""
Obligation Model for recurring payments (bills, EMIs, SIPs, insurance)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ObligationType(str, enum.Enum):
    CREDIT_CARD_BILL = "credit_card_bill"
    EMI = "emi"
    SIP = "sip"
    INSURANCE = "insurance"
    UTILITY = "utility"
    OTHER = "other"


class ObligationFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    ONE_TIME = "one_time"


class ObligationStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    obligation_type = Column(Enum(ObligationType), nullable=False, default=ObligationType.OTHER)
    amount = Column(Float, nullable=False)
    provider = Column(String, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False)
    next_due_date = Column(DateTime(timezone=True), nullable=True)
    frequency = Column(Enum(ObligationFrequency), nullable=False, default=ObligationFrequency.MONTHLY)
    autopay_enabled = Column(Boolean, default=False)
    status = Column(Enum(ObligationStatus), default=ObligationStatus.ACTIVE)
    extra_metadata = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="obligations")

