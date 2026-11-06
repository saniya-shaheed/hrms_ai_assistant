from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HRPoliciesBase(BaseModel):
    policy_code : str
    policy_title : str
    policy_category : str
    description : str | None = None
    department_id : int | None = None
    owner_user_id : int | None = None
    status : str = "active"

class HRPoliciesCreate(HRPoliciesBase):
    pass

class HRPoliciesUpdate(HRPoliciesBase):
    policy_code : str | None = None
    policy_title : str | None = None
    policy_category : str | None = None

class HRPoliciesOut(HRPoliciesBase):
    model_config = ConfigDict(from_attributes=True)
    policy_id : int
    created_at : datetime
    updated_at : datetime


