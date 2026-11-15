from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HRDocumentRequestHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    history_id: int
    document_request_id: int
    previous_status: str | None
    new_status: str
    action_by_user_id: int | None
    comments: str | None
    action_at: datetime