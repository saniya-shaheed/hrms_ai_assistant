from datetime import datetime

from pydantic import BaseModel


class LeaveEntitlementRulesBase(BaseModel):
    leave_type_id : int
    employment_category : str
    entitlement_days : int
    effective_from : datetime
    effective_to : datetime
    is_active : bool = True

class LeaveEntitlementRulesCreate(LeaveEntitlementRulesBase):
    pass

class LeaveEntitlementRulesBase(BaseModel):
    leave_type_id : int | None = None
    employment_category : str | None = None
    entitlement_days : int | None = None
    effective_from : datetime | None = None
    effective_to : datetime | None = None

class LeaveEntitlementRulesOut(LeaveEntitlementRulesBase):
    entitlement_rule_id : int
    created_at : datetime
    updated_at : datetime



