from sqlalchemy.orm import Session

from app.models.ai_messages import AIMessages

def create_message(
    db: Session,
    conversation_id: int,
    sender_type: str,
    content: str,
    model_name: str | None = None,
    token_count: int | None = None,
    meta_data: dict | None = None
):
    message = AIMessages(
        conversation_id=conversation_id,
        sender_type=sender_type,
        content=content,
        model_name=model_name,
        token_count=token_count,
        meta_data=meta_data or {}
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(AIMessages)
        .filter(
            AIMessages.conversation_id == conversation_id
        )
        .order_by(
            AIMessages.created_at.asc(),
            AIMessages.message_id.asc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

