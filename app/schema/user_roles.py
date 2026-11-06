from datetime import datetime

from pydantic import BaseModel


class UserRolesBase(BaseModel):
    user_id : int
    role_id : int

class UserRolesCreate(UserRolesBase):
    pass

class UserRolesUpdate(UserRolesBase):
    user_id : int | None = None 
    role_id : int | None = None

class UserRolesOut(UserRolesBase):
    model_config = ConfigDict(from_attributes=True)
    assigned_at : datetime


