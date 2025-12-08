"""
Recommendation Service with AI-powered Product Matching
"""
from typing import Optional
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.product import Product, ProductType, RiskLevel
from app.models.goal import Goal
from app.models.user import User
from app.schemas.product import ProductRecommendation
from app.services.ai_service import AIService

class RecommendationService:
    def __init__(self):
        self.ai_service = AIService()
    
    async def get_recommendations(
        self, 
        db: Session, 
        user_id: int,
        goal_id: Optional[int] = None,
        limit: int = 5
    ) -> List[ProductRecommendation]:
        """Get personalized product recommendations"""
        # Get user profile
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        user_profile = {
            "age": user.age,
            "income": user.income,
            "risk_tolerance": user.risk_tolerance
        }
        
        # Optional goal context
        goal = None
        goal_horizon_months = None
        if goal_id:
            goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
            if goal and goal.target_date:
                delta_days = (goal.target_date - goal.created_at).days if goal.created_at else None
                if delta_days and delta_days > 0:
                    goal_horizon_months = max(delta_days / 30, 1)

        # Get all products
        products = db.query(Product).all()
        
        recommendations = []
        for product in products:
            # Basic matching logic
            match_score = self._calculate_match_score(product, user_profile, goal_horizon_months)
            
            if match_score > 0.5:  # Only recommend if match > 50%
                # Generate AI reasoning
                reasoning = await self.ai_service.generate_recommendation_reasoning(
                    {
                        "name": product.name,
                        "type": product.product_type.value,
                        "risk_level": product.risk_level.value,
                        "expected_return": product.expected_return,
                        "min_investment": product.min_investment
                    },
                    user_profile
                )
                
                # Determine suitability factors
                suitability_factors = self._get_suitability_factors(product, user_profile, goal_horizon_months)
                
                recommendation = ProductRecommendation(
                    product=product,
                    match_score=match_score,
                    reasoning=reasoning,
                    suitability_factors=suitability_factors,
                    recommended_investment=self._calculate_recommended_investment(
                        product, user_profile
                    )
                )
                recommendations.append(recommendation)
        
        # Sort by match score
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:limit]
    
    def _calculate_match_score(self, product: Product, user_profile: Dict, goal_horizon_months: Optional[float]) -> float:
        """Calculate match score between product and user"""
        score = 0.5  # Base score
        
        # Risk tolerance matching
        risk_mapping = {
            "conservative": RiskLevel.LOW,
            "moderate": RiskLevel.MEDIUM,
            "aggressive": RiskLevel.HIGH
        }
        
        user_risk = risk_mapping.get(user_profile.get("risk_tolerance", "moderate"))
        if product.risk_level == user_risk:
            score += 0.3
        elif abs(ord(product.risk_level.value[0]) - ord(user_risk.value[0])) == 1:
            score += 0.15
        
        # Income-based matching
        if user_profile.get("income"):
            if product.min_investment and product.min_investment <= user_profile["income"] * 0.1:
                score += 0.1
            elif not product.min_investment:
                score += 0.1
        
        # Age-based matching
        age = user_profile.get("age", 30)
        if age < 30 and product.product_type in [ProductType.MUTUAL_FUND, ProductType.SIP]:
            score += 0.1
        elif age > 50 and product.product_type in [ProductType.FD, ProductType.PPF]:
            score += 0.1

        # Goal horizon bias
        if goal_horizon_months:
            if goal_horizon_months <= 12:
                if product.product_type in [ProductType.FD, ProductType.RD, ProductType.CREDIT_CARD]:
                    score += 0.1
            else:
                if product.product_type in [ProductType.MUTUAL_FUND, ProductType.SIP, ProductType.INSURANCE, ProductType.PPF]:
                    score += 0.1

        # Credit card suitability
        if product.product_type == ProductType.CREDIT_CARD:
            if user_profile.get("income") and product.annual_fee and product.annual_fee < user_profile["income"] * 0.02:
                score += 0.05
            if product.rewards_type:
                score += 0.05
        
        return min(score, 1.0)
    
    def _get_suitability_factors(self, product: Product, user_profile: Dict, goal_horizon_months: Optional[float]) -> List[str]:
        """Get suitability factors for a product"""
        factors = []
        
        risk_mapping = {
            "conservative": "low risk",
            "moderate": "moderate risk",
            "aggressive": "high risk"
        }
        
        user_risk = user_profile.get("risk_tolerance", "moderate")
        if product.risk_level.value == risk_mapping.get(user_risk, "moderate risk"):
            factors.append(f"Matches your {user_risk} risk tolerance")
        
        if product.expected_return:
            factors.append(f"Expected return: {product.expected_return}% annually")
        
        if product.min_investment and user_profile.get("income"):
            if product.min_investment <= user_profile["income"] * 0.1:
                factors.append("Affordable minimum investment")

        if goal_horizon_months:
            horizon_label = "short-term" if goal_horizon_months <= 12 else "long-term"
            factors.append(f"Aligned to {horizon_label} horizon")

        if product.product_type == ProductType.CREDIT_CARD:
            if product.annual_fee is not None:
                factors.append(f"Annual fee: {product.annual_fee}")
            if product.rewards_type:
                factors.append(f"Rewards focus: {product.rewards_type}")
            if product.welcome_bonus:
                factors.append(f"Welcome bonus: {product.welcome_bonus}")
        
        return factors
    
    def _calculate_recommended_investment(
        self, 
        product: Product, 
        user_profile: Dict
    ) -> Optional[float]:
        """Calculate recommended investment amount"""
        income = user_profile.get("income")
        if not income:
            return None
        
        # Recommend 10-20% of monthly income for investments
        if product.min_investment:
            return max(product.min_investment, income * 0.1)
        return income * 0.15

