from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LeaveTypesBase(BaseModel):
    leave_type_code: str = Field(min_length=1, max_length=50)
    leave_type_name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    is_paid: bool = True
    requires_approval: bool = True
    min_notice_calender_days: int = Field(default=0, ge=0)
    max_consecutive_days: int | None = Field(default=None, ge=1)
    is_active: bool = True


class LeaveTypesCreate(LeaveTypesBase):
    pass


class LeaveTypesUpdate(BaseModel):
    leave_type_code: str | None = Field(
        default=None, min_length=1, max_length=50
    )
    leave_type_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    description: str | None = None
    is_paid: bool | None = None
    requires_approval: bool | None = None
    min_notice_calender_days: int | None = Field(
        default=None, ge=0
    )
    max_consecutive_days: int | None = Field(
        default=None, ge=1
    )
    is_active: bool | None = None


class LeaveTypesOut(LeaveTypesBase):
    model_config = ConfigDict(from_attributes=True)

    leave_type_id: int
    created_at: datetime
    updated_at: datetime