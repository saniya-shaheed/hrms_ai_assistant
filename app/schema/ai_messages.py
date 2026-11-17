from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIMessageOut(BaseModel):
    message_id: int
    conversation_id: int
    sender_type: str
    content: str
    model_name: str | None = None
    token_count: int | None = None
    meta_data: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)