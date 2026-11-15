from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TimesheetDecisionRequest(BaseModel):
    decision: Literal["Approved", "Rejected"]
    comments: str | None = Field(
        default=None,
        max_length=2000
    )


class TimesheetApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timesheet_approval_id: int
    timesheet_id: int
    approver_employee_id: int
    decision: str
    comments: str | None
    decided_at: datetime
    created_at: datetime