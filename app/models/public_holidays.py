from datetime import date
from sqlalchemy import Boolean, Column, Date, Integer, String
from app.database import Base

class PublicHolidays(Base):
    __tablename__ = "public_holidays"

    public_holiday_id = Column(Integer, primary_key=True, nullable=False, index=True)
    holiday_date = Column(Date, nullable=False)
    holiday_name = Column(String(100), nullable=False)
    country_code = Column(String(100), nullable=False, default="AE")
    region = Column(String(100), nullable=False, default="All")
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)


    