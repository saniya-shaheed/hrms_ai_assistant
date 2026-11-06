from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeaveTypesBase(BaseModel):
    leave_type_code : str
    leave_type_name : str
    description : str | None = None
    is_paid : bool = True
    requires_approval : bool = True
    min_notice_calender_days : int = 0
    max_consecutive_days : int = 0
    is_active : bool =True

class LeaveTypesCreate(LeaveTypesBase):
    pass

class LeaveTypesUpdate(LeaveTypesBase):
    leave_type_code : str | None = None
    leave_type_name : str | None = None
    description : str | None = None

class LeaveTypesOut(LeaveTypesBase):
    model_config = ConfigDict(from_attributes=True)
    leave_type_id : int
    created_at : datetime
    updated_at : datetime


