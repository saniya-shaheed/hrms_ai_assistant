from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HRDocumentTypesCreate(BaseModel):
    document_type_code: str = Field(
        min_length=1,
        max_length=100
    )
    document_type_name: str = Field(
        min_length=1,
        max_length=200
    )
    description: str | None = None
    requires_hr_approval: bool = True
    is_active: bool = True


class HRDocumentTypesUpdate(BaseModel):
    document_type_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    document_type_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    description: str | None = None
    requires_hr_approval: bool | None = None
    is_active: bool | None = None


class HRDocumentTypesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type_id: int
    document_type_code: str
    document_type_name: str
    description: str | None
    requires_hr_approval: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime