from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LeaveTransactionsBase(BaseModel):
    employee_id : int
    leave_balance_id : int
    leave_request_id : int | None = None
    transaction_type : str
    days_delta : int 
    notes : str | None = None
    actor_user_id : int | None = None

class LeaveTransactionsCreate(LeaveTransactionsBase):
    pass

class LeaveTransactionsUpdate(LeaveTransactionsBase):
    employee_id : int | None = None
    leave_balance_id : int | None = None
    transaction_type : str | None = None
    days_delta : int | None = None

class LeaveTransactionsCreate(LeaveTransactionsBase):
    model_config = ConfigDict(from_attributes=True)
    leave_transaction_id : int
    created_at : datetime


