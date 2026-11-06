
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class LeaveApprovalsBase(BaseModel):
    leave_request_id : int
    approver_employee_id : int
    decision : str
    comments : str | None = None
    decided_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeaveApprovalsCreate(LeaveApprovalsBase):
    pass

class LeaveApprovalsUpdate(LeaveApprovalsBase):
    leave_request_id : int | None = None
    approver_employee_id : int | None = None
    decision : str | None = None
    decided_at : datetime | None = None

class LeaveApprovalsOut(LeaveApprovalsBase):
    model_config = ConfigDict(from_attributes=True)
    leave_approval_id : int
    created_at : datetime
