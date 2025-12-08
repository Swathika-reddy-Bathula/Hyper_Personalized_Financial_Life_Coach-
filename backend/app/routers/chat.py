"""
Chat Router for conversational interface
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.ai_service import AIService
from app.core.security import get_current_user
from app.models.conversation import Conversation, Message

router = APIRouter()
ai_service = AIService()

@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the AI financial assistant"""
    # Build user context
    context = {
        "user_id": current_user.id,
        "age": current_user.age,
        "income": current_user.income,
        "risk_tolerance": current_user.risk_tolerance
    }
    
    # Get user goals for context
    from app.models.goal import Goal
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).limit(5).all()
    context["goals"] = [
        {"title": g.title, "target_amount": g.target_amount, "current_amount": g.current_amount}
        for g in goals
    ]
    
    # Merge with provided context
    if message.context:
        context.update(message.context)
    
    conversation: Conversation
    if message.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == message.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title=message.message[:80]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Load history
    history_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).all()
    history_payload = [
        {"role": m.role, "content": m.content} for m in history_messages
    ]

    # Persist user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=message.message
    )
    db.add(user_msg)
    db.commit()

    # Get AI response
    response = await ai_service.chat_response(message.message, context, history_payload)

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response["response"],
        reasoning=response.get("reasoning")
    )
    db.add(assistant_msg)
    db.commit()

    # Reload history for response
    latest_history = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).all()

    return ChatResponse(
        response=response["response"],
        reasoning=response.get("reasoning"),
        suggestions=response.get("suggestions"),
        confidence=response.get("confidence"),
        conversation_id=conversation.id,
        history=[
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "reasoning": m.reasoning,
                "created_at": m.created_at
            }
            for m in latest_history
        ]
    )

