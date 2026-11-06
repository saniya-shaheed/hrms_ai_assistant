from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PublicHolidaysBase(BaseModel):
    holiday_date : datetime
    holiday_name : str
    country_code : str = "AE"
    region : str = "All"
    is_active : bool = True

class PublicHolidaysCreate(PublicHolidaysBase):
    pass

class PublicHolidaysUpdate(PublicHolidaysBase):
    holiday_date : datetime | None = None
    holiday_name : str | None = None

class PublicHolidaysOut(PublicHolidaysBase):
    model_config = ConfigDict(from_attributes=True)
    public_holiday_id : int
    created_at : datetime
    updated_at : datetime

