from datetime import datetime, timezone

from pydantic import BaseModel, Field


class TimesheetApprovalsBase(BaseModel):
    timesheet_id : int
    approver_employee_id : int
    decision : str
    comments : str | None = None
    decided_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimesheetApprovalsCreate(TimesheetApprovalsBase):
    pass

class TimesheetApprovalsUpdate(TimesheetApprovalsBase):
    timesheet_id : int | None = None
    approver_employee_id : int | None = None
    decision : str | None = None
    decided_at : datetime | None = None

class TimesheetApprovals(TimesheetApprovalsBase):
    timesheet_approval_id : int
    created_at : datetime


    


