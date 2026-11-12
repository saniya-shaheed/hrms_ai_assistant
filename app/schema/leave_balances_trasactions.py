from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class LeaveBalancesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leave_balance_id: int
    employee_id: int
    leave_type_code: str
    entitlement_days: int
    used_days: int
    available_days: int
    balance_year: int
    created_at: datetime | None
    updated_at: datetime | None


class LeaveBalanceAdjustment(BaseModel):
    days_delta: int = Field(ne=0)
    reason: str = Field(min_length=3, max_length=1000)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Adjustment reason cannot be empty")

        return value


class LeaveBalanceAdjustmentOut(BaseModel):
    balance: LeaveBalancesOut
    transaction: "LeaveTransactionsOut"


class LeaveTransactionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leave_transaction_id: int
    employee_id: int
    leave_balance_id: int
    leave_request_id: int | None
    transaction_type: str
    days_delta: int
    notes: str | None
    actor_user_id: int | None
    created_at: datetime | None