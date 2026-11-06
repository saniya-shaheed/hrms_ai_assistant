from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HRDocumentRequestHistoryBase(BaseModel):
    document_request_id : int
    previous_status : str | None = None
    new_status : str
    action_by_user_id : int | None = None
    comments : str | None = None

class HRDocumentRequestHistoryCreate(HRDocumentRequestHistoryBase):
    pass

class HRDocumentRequestHistoryUpdate(HRDocumentRequestHistoryBase):
    document_request_id : int | None = None
    new_status : str | None = None

class HRDocumentRequestHistoryOut(HRDocumentRequestHistoryBase):
    model_config = ConfigDict(from_attributes=True)
    history_id : int
    action_at : datetime


