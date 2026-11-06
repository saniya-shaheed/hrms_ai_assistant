from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeaveBalancesBase(BaseModel):
    employee_id : int
    leave_type_code : str
    entitlement_days : int = 0
    used_days : int = 0
    balance_year : int

class LeaveBalancesCreate(LeaveBalancesBase):
    pass

class LeaveBalancesUpdate(LeaveBalancesBase):
    employee_id : int | None = None
    leave_type_code : str | None = None
    balance_year : int | None = None

class LeaveBalancesOut(LeaveBalancesBase):
    model_config = ConfigDict(from_attributes = True)
    leave_balance_id : int
    created_at : datetime
    updated_at : datetime



