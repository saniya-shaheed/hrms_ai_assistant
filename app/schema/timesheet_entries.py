from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class TimesheetEntryCreate(BaseModel):
    work_date: date
    hours_worked: int = Field(ge=1, le=24)
    task_description: str | None = None
    project_code: str | None = Field(
        default=None,
        max_length=100
    )


class TimesheetEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timesheet_entry_id: int
    timesheet_id: int
    work_date: date
    hours_worked: int
    task_description: str | None
    project_code: str | None
    created_at: datetime
    updated_at: datetime