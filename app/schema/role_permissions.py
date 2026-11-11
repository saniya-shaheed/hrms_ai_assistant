from pydantic import BaseModel, ConfigDict


class RolePermissionsBase(BaseModel):
    permission_id : int

class RolePermissionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: int
    permission_id : int

