from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LeaveDecisionRequest(BaseModel):
    decision: Literal["Approved", "Rejected"]
    comments: str | None = Field(default=None, max_length=2000)


class LeaveApprovalsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leave_approval_id: int
    leave_request_id: int
    approver_employee_id: int
    decision: Literal["Approved", "Rejected"]
    comments: str | None
    decided_at: datetime
    created_at: datetime