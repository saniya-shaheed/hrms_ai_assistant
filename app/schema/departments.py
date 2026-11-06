
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DepartmentsBase(BaseModel):
    department_name: str
    department_code: str
    parent_department_id: int | None = None
    is_active: bool = True


class DepartmentCreate(DepartmentsBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: str | None = None
    department_code: str | None = None
    parent_department_id: int | None = None
    is_active: bool | None = None


class DepartmentOut(DepartmentsBase):
    model_config = ConfigDict(from_attributes=True)

    department_id: int
    created_at: datetime
    updated_at: datetime
