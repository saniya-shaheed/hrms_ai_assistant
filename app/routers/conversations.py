from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies.auth import get_current_user

from app.crud.ai_conversations import (
    create_conversation,
    get_user_conversations,
    get_conversation_by_id
)

from app.crud.ai_messages import get_conversation_messages

from app.schema.ai_conversations import (
    AIConversationCreate,
    AIConversationOut
)

from app.schema.ai_messages import AIMessageOut


router = APIRouter(
    prefix="/conversations",
    tags=["AI Assistant"]
)


# --------------------------------------------------
# 1. CREATE CONVERSATION
# POST /conversations
# --------------------------------------------------

@router.post(
    "",
    response_model=AIConversationOut,
    status_code=status.HTTP_201_CREATED
)
def create_new_conversation(
    conversation_data: AIConversationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return create_conversation(
        db,
        user_id=current_user.user_id,
        title=conversation_data.title
    )


# --------------------------------------------------
# 2. GET USER CONVERSATIONS
# GET /conversations
# --------------------------------------------------

@router.get(
    "",
    response_model=list[AIConversationOut]
)
def list_my_conversations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    return get_user_conversations(
        db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 3. GET CONVERSATION MESSAGES
# GET /conversations/{conversation_id}/messages
# --------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=list[AIMessageOut]
)
def get_conversation_history(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    # Verify conversation ownership
    conversation = get_conversation_by_id(
        db,
        conversation_id,
        current_user.user_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return get_conversation_messages(
        db,
        conversation_id,
        skip=skip,
        limit=limit
    )