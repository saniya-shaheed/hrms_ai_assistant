import os
from datetime import date, timedelta

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.public_holidays import PublicHolidays


load_dotenv()


# Read organisation working days from .env
try:
    WORKING_WEEKDAYS = {
        int(day.strip())
        for day in os.getenv(
            "HRMS_WORKING_WEEKDAYS",
            "0,1,2,3,4"
        ).split(",")
    }

    if not WORKING_WEEKDAYS or any(
        day < 0 or day > 6
        for day in WORKING_WEEKDAYS
    ):
        raise ValueError

except ValueError:
    raise ValueError(
        "HRMS_WORKING_WEEKDAYS must contain weekday numbers from 0 to 6"
    )


HOLIDAY_COUNTRY_CODE = os.getenv(
    "HRMS_HOLIDAY_COUNTRY_CODE",
    "AE"
)

HOLIDAY_REGION = os.getenv(
    "HRMS_HOLIDAY_REGION",
    "All"
)


def get_working_days(
    db: Session,
    start_date: date,
    end_date: date
) -> int:

    if end_date < start_date:
        raise ValueError(
            "End date cannot be earlier than start date"
        )

    # Determine which holiday regions apply
    regions = (
        ["All"]
        if HOLIDAY_REGION == "All"
        else ["All", HOLIDAY_REGION]
    )

    # Retrieve applicable active holidays
    holidays = (
        db.query(PublicHolidays.holiday_date)
        .filter(
            PublicHolidays.holiday_date >= start_date,
            PublicHolidays.holiday_date <= end_date,
            PublicHolidays.country_code == HOLIDAY_COUNTRY_CODE,
            PublicHolidays.region.in_(regions),
            PublicHolidays.is_active.is_(True)
        )
        .all()
    )

    holiday_dates = {
        holiday.holiday_date
        for holiday in holidays
    }

    working_days = 0
    current_date = start_date

    while current_date <= end_date:

        is_working_weekday = (
            current_date.weekday() in WORKING_WEEKDAYS
        )

        is_public_holiday = (
            current_date in holiday_dates
        )

        if is_working_weekday and not is_public_holiday:
            working_days += 1

        current_date += timedelta(days=1)

    return working_days