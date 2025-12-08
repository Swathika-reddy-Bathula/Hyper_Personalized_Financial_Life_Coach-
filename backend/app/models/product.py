"""
Financial Product Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base

class ProductType(str, enum.Enum):
    MUTUAL_FUND = "mutual_fund"
    SIP = "sip"
    FD = "fixed_deposit"
    RD = "recurring_deposit"
    STOCK = "stock"
    BOND = "bond"
    INSURANCE = "insurance"
    PPF = "ppf"
    CREDIT_CARD = "credit_card"
    OTHER = "other"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product_type = Column(Enum(ProductType), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String, nullable=True)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    min_investment = Column(Float, nullable=True)
    expected_return = Column(Float, nullable=True)  # Annual percentage
    lock_in_period = Column(Integer, nullable=True)  # In months
    features = Column(Text, nullable=True)  # JSON string
    eligibility_criteria = Column(Text, nullable=True)  # JSON string
    # Credit card specific fields (optional)
    issuer = Column(String, nullable=True)
    annual_fee = Column(Float, nullable=True)
    rewards_type = Column(String, nullable=True)
    welcome_bonus = Column(String, nullable=True)
    intro_apr_months = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

