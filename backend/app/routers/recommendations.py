"""
Recommendations Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductRecommendation
from app.services.recommendation_service import RecommendationService
from app.core.security import get_current_user

router = APIRouter()
recommendation_service = RecommendationService()

@router.get("", response_model=List[ProductRecommendation])
async def get_recommendations(
    goal_id: Optional[int] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized product recommendations with XAI reasoning"""
    recommendations = await recommendation_service.get_recommendations(
        db, current_user.id, goal_id, limit
    )
    return recommendations

@router.get("/products", response_model=List[dict])
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all available financial products"""
    from app.models.product import Product
    from app.schemas.product import ProductResponse
    
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductResponse.model_validate(p).model_dump() for p in products]

