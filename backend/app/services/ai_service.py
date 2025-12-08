"""
AI Service using LangChain and OpenAI
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import json
from app.core.config import settings

class AIService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
    
    async def understand_goal(self, user_input: str, user_context: Dict) -> Dict:
        """Extract and understand financial goals from natural language"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a financial planning assistant. 
            Extract financial goals from user input and create a structured plan.
            Return a JSON object with: title, description, goal_type, target_amount, target_date, monthly_contribution, reasoning.
            Consider user's income, age, and risk tolerance when creating the plan."""),
            HumanMessage(content=f"""
            User Input: {user_input}
            User Context: {json.dumps(user_context)}
            
            Extract the financial goal and create a detailed plan with reasoning.
            """)
        ])
        
        messages = prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        try:
            return json.loads(response.content)
        except:
            # Fallback parsing
            return {"reasoning": response.content, "goal_data": {}}
    
    async def analyze_spending(self, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns and suggest savings"""
        transactions_summary = json.dumps(transactions[:50])  # Limit for token usage
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a financial behavior analyst.
            Analyze spending patterns and provide actionable savings suggestions.
            Return JSON with: insights, categories_analysis, savings_opportunities, recommendations."""),
            HumanMessage(content=f"""
            Transactions: {transactions_summary}
            
            Analyze spending patterns and provide detailed insights with specific recommendations.
            """)
        ])
        
        messages = prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        try:
            return json.loads(response.content)
        except:
            return {"insights": response.content, "recommendations": []}
    
    async def generate_recommendation_reasoning(
        self, 
        product: Dict, 
        user_profile: Dict
    ) -> str:
        """Generate explainable reasoning for product recommendations"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a financial advisor providing explainable recommendations.
            Explain why a product is suitable for the user in clear, understandable terms."""),
            HumanMessage(content=f"""
            Product: {json.dumps(product)}
            User Profile: {json.dumps(user_profile)}
            
            Provide a detailed explanation of why this product is recommended, including:
            1. Match with user's risk tolerance
            2. Alignment with financial goals
            3. Expected benefits
            4. Any considerations or risks
            """)
        ])
        
        messages = prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def chat_response(
        self,
        message: str,
        context: Optional[Dict] = None,
        history: Optional[List[Dict]] = None
    ) -> Dict:
        """Generate chat response with short conversation history for context"""
        context_str = json.dumps(context) if context else "No additional context"
        history = history or []
        formatted_history = "\n".join(
            [f"{turn['role']}: {turn['content']}" for turn in history[-10:]]
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a helpful financial assistant.
            Provide clear, actionable financial advice. Always explain your reasoning.
            Be empathetic and supportive. Keep answers concise and numbered when listing steps."""),
            HumanMessage(content=f"""
            Recent History:
            {formatted_history or "No prior messages"}

            User Message: {message}
            Context: {context_str}
            
            Provide a helpful response with clear reasoning.
            """)
        ])
        
        messages = prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        return {
            "response": response.content,
            "reasoning": "Grounded in your profile and conversation history",
            "confidence": 0.85
        }

