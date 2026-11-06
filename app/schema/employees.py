from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmployeesBase(BaseModel):
    employee_code : str
    employee_name : str
    email : str
    department_id : int | None = None
    job_title : str | None = None
    hire_date : datetime | None = None
    is_active : bool = True
    manager_employee_id : int | None = None

class EmployeesCreate(EmployeesBase):
    pass

class EmployeesUpdate(EmployeesBase):
    employee_code : str | None = None
    employee_name : str | None = None
    email : str | None = None

class EmployeesOut(EmployeesBase):
    model_config = ConfigDict(from_attributes=True)
    employee_id : int
    created_at : datetime
    updated_at : datetime




