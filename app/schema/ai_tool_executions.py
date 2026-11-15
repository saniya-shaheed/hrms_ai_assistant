from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AIToolExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tool_execution_id: int
    conversation_id: int
    message_id: int | None
    user_id: int | None
    tool_name: str
    input_arguments: dict[str, Any]
    execution_status: str
    result_summary: str | None
    error_code: str | None
    started_at: datetime
    completed_at: datetime | None