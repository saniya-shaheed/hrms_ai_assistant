from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UsersBase(BaseModel):
    employee_id: int
    is_active: bool = True


class UserCreate(UsersBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    is_active: bool | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime