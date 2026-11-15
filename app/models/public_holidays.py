from sqlalchemy import Boolean, Column, Date, BigInteger, String, DateTime, UniqueConstraint, func
from app.database import Base

class PublicHolidays(Base):
    __tablename__ = "public_holidays"

    __table_args__ = (
        UniqueConstraint(
            "holiday_date",
            "country_code",
            "region",
            name="uq_public_holiday_date_country_region"
        ),
    )

    public_holiday_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    holiday_date = Column(Date, nullable=False)
    holiday_name = Column(String(100), nullable=False)
    country_code = Column(String(100), nullable=False, default="AE")
    region = Column(String(100), nullable=False, default="All")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


    