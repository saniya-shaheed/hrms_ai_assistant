from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HRDocumentTypesBase(BaseModel):
    document_type_code : str
    document_type_name : str
    description : str | None = None
    requires_hr_approval : bool = True
    is_active : bool = True

class HRDocumentTypesCreate(HRDocumentTypesBase):
    pass

class HRDocumentTypesUpdate(HRDocumentTypesBase):
    document_type_code : str | None = None
    document_type_name : str | None = None

class HRDocumentTypesOut(HRDocumentTypesBase):
    model_config = ConfigDict(from_attributes=True)
    document_type_id : int
    created_at : datetime
    updated_at : datetime



