from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class LeaveEntitlementRulesCreate(BaseModel):
    leave_type_id: int = Field(gt=0)
    employment_category: str = Field(
        default="All",
        min_length=1,
        max_length=100
    )
    entitlement_days: int = Field(ge=0)
    effective_from: date
    effective_to: date | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.effective_to is not None
            and self.effective_to < self.effective_from
        ):
            raise ValueError(
                "Effective to date cannot be earlier than effective from date"
            )

        return self


class LeaveEntitlementRulesUpdate(BaseModel):
    leave_type_id: int | None = Field(default=None, gt=0)
    employment_category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    entitlement_days: int | None = Field(default=None, ge=0)
    effective_from: date | None = None
    effective_to: date | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_to < self.effective_from
        ):
            raise ValueError(
                "Effective to date cannot be earlier than effective from date"
            )

        return self


class LeaveEntitlementRulesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entitlement_rule_id: int
    leave_type_id: int
    employment_category: str
    entitlement_days: int
    effective_from: date
    effective_to: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime