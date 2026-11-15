from sqlalchemy.orm import Session

from app.models.ai_messages import AIMessages


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