from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRolesBase(BaseModel):
    role_id : int
class UserRolesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id : int
    role_id : int
    assigned_at : datetime


