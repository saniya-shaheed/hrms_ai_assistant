from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HRDocumentRequestCreate(BaseModel):
    document_type_code: str = Field(
        min_length=1,
        max_length=100
    )
    purpose: str | None = None


class HRDocumentRequestUpdate(BaseModel):
    status: Literal[
        "Processing",
        "Completed",
        "Rejected"
    ] | None = None

    remarks: str | None = None
    document_reference: str | None = Field(
        default=None,
        max_length=500
    )


class HRDocumentRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_request_id: int
    employee_id: int
    document_type_code: str
    purpose: str | None
    status: str
    requested_at: datetime
    processed_by_employee_id: int | None
    processed_at: datetime | None
    remarks: str | None
    document_reference: str | None