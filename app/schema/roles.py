from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RolesBase(BaseModel):
    role_name : str
    description : str | None = None

class RolesCreate(RolesBase):
    pass

class RolesUpdate(RolesBase):
    role_name : str | None = None

class RolesOut(RolesBase):
    model_config = ConfigDict(from_attributes=True)
    role_id : int
    created_at : datetime











