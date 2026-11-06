from pydantic import BaseModel


class RolePermissionsBase(BaseModel):
    role_id : int
    permission_id : int

class RolePermissionsCreate(RolePermissionsBase):
    pass

class RolePermissionsUpdate(BaseModel):
    role_id : int | None = None
    permission_id : int | None = None

class RoelPermissionsOut(RolePermissionsBase):
    pass

