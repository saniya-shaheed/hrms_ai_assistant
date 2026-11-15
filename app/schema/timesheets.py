from datetime import date, datetime, timedelta

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)

from app.schema.timesheet_entries import TimesheetEntryOut


class TimesheetCreate(BaseModel):
    period_start: date
    period_end: date
    employee_comments: str | None = None

    @model_validator(mode="after")
    def validate_weekly_period(self):
        if self.period_end < self.period_start:
            raise ValueError(
                "Period end cannot be earlier than period start"
            )

        if self.period_end - self.period_start != timedelta(days=6):
            raise ValueError(
                "A timesheet must cover exactly seven consecutive calendar days"
            )

        return self


class TimesheetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timesheet_id: int
    employee_id: int
    period_start: date
    period_end: date
    status: str
    submitted_at: datetime | None
    approved_at: datetime | None
    total_hours: int
    employee_comments: str | None
    reviewer_comments: str | None
    created_at: datetime
    updated_at: datetime

    # Include work entries when retrieving a timesheet.
    timesheet_entries: list[TimesheetEntryOut] = Field(
        default_factory=list
    )