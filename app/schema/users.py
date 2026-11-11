from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    employee_id: int = Field(gt=0)
    password: str = Field(min_length=8)
    is_active: bool = True


class UserUpdate(BaseModel):
    employee_id: int | None = Field(default=None, gt=0)


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserPasswordReset(BaseModel):
    new_password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime