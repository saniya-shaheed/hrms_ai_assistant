from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: int
    conversation_id: int
    sender_type: str
    content: str
    model_name: str | None
    token_count: int | None
    created_at: datetime