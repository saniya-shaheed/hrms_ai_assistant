from sqlalchemy.orm import Session

from app.models.ai_conversations import AIConversations


def create_conversation(
    db: Session,
    user_id: int,
    title: str | None = None
):
    conversation = AIConversations(
        user_id=user_id,
        title=title,
        status="active",
        meta_data={}
    )

    try:
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    except Exception:
        db.rollback()
        raise


def get_user_conversations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(AIConversations)
        .filter(AIConversations.user_id == user_id)
        .order_by(
            AIConversations.started_at.desc(),
            AIConversations.conversation_id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_conversation_by_id(
    db: Session,
    conversation_id: int,
    user_id: int
):
    return (
        db.query(AIConversations)
        .filter(
            AIConversations.conversation_id == conversation_id,
            AIConversations.user_id == user_id
        )
        .first()
    )