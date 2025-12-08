"""
Product Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductType, RiskLevel

class ProductResponse(BaseModel):
    id: int
    name: str
    product_type: ProductType
    description: Optional[str] = None
    provider: Optional[str] = None
    risk_level: RiskLevel
    min_investment: Optional[float] = None
    expected_return: Optional[float] = None
    lock_in_period: Optional[int] = None
    features: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    issuer: Optional[str] = None
    annual_fee: Optional[float] = None
    rewards_type: Optional[str] = None
    welcome_bonus: Optional[str] = None
    intro_apr_months: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductRecommendation(BaseModel):
    product: ProductResponse
    match_score: float  # 0-1
    reasoning: str  # XAI explanation
    suitability_factors: List[str]
    recommended_investment: Optional[float] = None

