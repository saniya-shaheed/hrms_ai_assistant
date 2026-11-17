from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import Users
from app.schema.ai_chat import AIChatRequest, AIChatResponse
from app.crud.ai_conversations import get_conversation_by_id
from app.crud.ai_messages import (
    create_message,
    get_conversation_messages
)
from app.services.gemini_service import GeminiService


router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)


@router.post(
    "",
    response_model=AIChatResponse,
    status_code=status.HTTP_200_OK
)
def chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=request.conversation_id,
        user_id=current_user.user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get previous messages from this conversation
    previous_messages = get_conversation_messages(
        db=db,
        conversation_id=request.conversation_id
    )

    # Convert database messages into Gemini conversation format
    history = []

    for message in previous_messages:

        if message.sender_type == "USER":
            role = "user"

        elif message.sender_type == "ASSISTANT":
            role = "model"

        else:
            continue

        history.append(
            {
                "role": role,
                "parts": [
                    {
                        "text": message.content
                    }
                ]
            }
        )

    # Save current user message
    user_message = create_message(
        db=db,
        conversation_id=request.conversation_id,
        sender_type="USER",
        content=request.message
    )

    # Generate response using previous conversation history
    gemini = GeminiService()

    response_text = gemini.generate_response(
        message=request.message,
        history=history
    )

    # Save assistant response
    assistant_message = create_message(
        db=db,
        conversation_id=request.conversation_id,
        sender_type="ASSISTANT",
        content=response_text,
        model_name=gemini.model_name
    )

    return AIChatResponse(
        conversation_id=request.conversation_id,
        user_message_id=user_message.message_id,
        assistant_message_id=assistant_message.message_id,
        response=response_text,
        model_name=gemini.model_name
    )