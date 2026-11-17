from pydantic import BaseModel


class AIChatRequest(BaseModel):
    conversation_id: int
    message: str


class AIChatResponse(BaseModel):
    conversation_id: int
    user_message_id: int
    assistant_message_id: int
    response: str
    model_name: str