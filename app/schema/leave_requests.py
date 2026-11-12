from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class LeaveRequestsCreate(BaseModel):
    leave_type_code: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    reason: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError(
                "End date cannot be earlier than start date"
            )

        return self


class LeaveRequestsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    leave_request_id: int
    employee_id: int
    leave_type_code: str
    start_date: date
    end_date: date
    days_requested: int
    reason: str | None
    status: str
    submitted_at: datetime
    updated_at: datetime