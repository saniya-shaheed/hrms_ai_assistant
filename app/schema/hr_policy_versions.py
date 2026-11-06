from datetime import datetime

from pydantic import BaseModel


class HRPolicyVersionsBase(BaseModel):
    policy_id : int
    version_number : int
    version_label : str | None = None
    status : str = "draft" 
    effective_from : datetime | None = None
    effective_to : datetime | None = None
    submitted_at : datetime | None = None
    approved_by_user_id : int | None = None
    approved_at : datetime | None = None
    published_at : datetime | None = None
    source_file_name : str | None = None
    source_reference : str | None = None
    change_summary : str | None = None
    created_by_user_id : int | None = None

class HRPolicyVersionsCreate(HRPolicyVersionsBase):
    pass

class HRPolicyVersionsUpdate(HRPolicyVersionsBase):
    policy_id : int | None = None
    version_number : int | None = None

class HRPolicyVersionsOut(HRPolicyVersionsBase):
    policy_version_id : int
    created_at  : datetime
    updated_at : datetime





