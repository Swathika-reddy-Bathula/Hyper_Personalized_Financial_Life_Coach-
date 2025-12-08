"""
Chat Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    context: Optional[dict] = None


class ChatTurn(BaseModel):
    id: int
    role: str
    content: str
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None  # XAI explanation
    suggestions: Optional[List[str]] = None
    confidence: Optional[float] = None
    conversation_id: Optional[int] = None
    history: Optional[List[ChatTurn]] = None

