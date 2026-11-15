from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    conversation_id: int = Field(gt=0)
    message: str = Field(min_length=1)


class AIChatResponse(BaseModel):
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    response: str
    model_name: str | None = None