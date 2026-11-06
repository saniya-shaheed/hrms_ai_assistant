from datetime import datetime

from pydantic import BaseModel


class TimeSheetEntriesBase(BaseModel):
    timesheet_id : int
    work_date  : datetime
    hours_worked : int
    task_description : str | None = None
    project_code : str | None = None

class TimeSheetEntriesCreate(TimeSheetEntriesBase):
    pass

class TimeSheetEntriesUpdate(TimeSheetEntriesBase):
    timesheet_id : int | None = None
    work_date  : datetime | None = None
    hours_worked : int | None = None

class TimeSheetEntriesOut(TimeSheetEntriesBase):
    timesheet_entry_id : int
    created_at : datetime
    updated_at : datetime





