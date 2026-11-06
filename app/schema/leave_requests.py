
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeaveRequestsBase(BaseModel):
    employee_id : int
    leave_type_code : str
    start_date : datetime
    end_Date : datetime
    days_requested : int
    reason : str | None = None
    status : str = "Pending"

class LeaveRequestsCreate(LeaveRequestsBase):
    pass

class LeaveRequestsUpdate(LeaveRequestsBase):
    employee_id : int | None = None
    leave_type_code : str | None = None
    start_date : datetime | None = None
    end_Date : datetime | None = None
    days_requested : int | None = None

class LeaveRequestsOut(LeaveRequestsBase):
    model_config = ConfigDict(from_attributes=True)
    leave_request_id : int
    submitted_At : datetime
    updated_at : datetime

