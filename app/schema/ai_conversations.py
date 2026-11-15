from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIConversationCreate(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=200
    )


class AIConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: int
    user_id: int
    title: str | None
    status: str
    started_at: datetime
    last_message_at: datetime | None
    ended_at: datetime | None