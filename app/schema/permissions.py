from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PermissionsBase(BaseModel):
    permission_code : str
    description : str | None = None

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsUpdate(BaseModel):
    permission_code : str | None = None
    description : str | None = None

class PermissionsOut(PermissionsBase):
    model_config = ConfigDict(from_attributes=True)
    permission_id : int
    created_at : datetime









