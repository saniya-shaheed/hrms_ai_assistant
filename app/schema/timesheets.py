from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TimesheetsBase(BaseModel):
    employee_id : int
    period_start : datetime
    period_end : datetime
    status : str = "draft"
    submitted_at : datetime | None = None
    approved_at : datetime | None = None
    total_hours : int = 0
    employee_comments : str | None = None
    reviewer_comments : str | None = None

class TimesheetsCreate(TimesheetsBase):
    pass

class TimesheetsUpdate(TimesheetsBase):
    employee_id : int | None = None
    period_start : datetime | None = None
    period_end : datetime | None = None

class TimesheetsOut(TimesheetsBase):
    model_config = ConfigDict(from_attributes=True)
    timesheet_id : int
    created_at : datetime
    updated_at : datetime



