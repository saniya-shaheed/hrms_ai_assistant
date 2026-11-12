from datetime import date

from sqlalchemy.orm import Session

from app.models.public_holidays import PublicHolidays


def get_all_public_holidays(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    year: int | None = None,
    country_code: str | None = None,
    region: str | None = None
):
    query = db.query(PublicHolidays).filter(
        PublicHolidays.is_active.is_(True)
    )

    # Filter by year
    if year is not None:
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)

        query = query.filter(
            PublicHolidays.holiday_date >= year_start,
            PublicHolidays.holiday_date <= year_end
        )

    # Filter by country
    if country_code is not None:
        query = query.filter(
            PublicHolidays.country_code == country_code
        )

    # A region-specific search also includes holidays
    # applicable to all regions.
    if region is not None:
        if region == "All":
            query = query.filter(
                PublicHolidays.region == "All"
            )
        else:
            query = query.filter(
                PublicHolidays.region.in_(["All", region])
            )

    return (
        query
        .order_by(PublicHolidays.holiday_date)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_public_holiday_by_id(
    db: Session,
    holiday_id: int
):
    return (
        db.query(PublicHolidays)
        .filter(
            PublicHolidays.public_holiday_id == holiday_id
        )
        .first()
    )


def get_duplicate_public_holiday(
    db: Session,
    holiday_date: date,
    country_code: str,
    region: str,
    exclude_holiday_id: int | None = None
):
    query = db.query(PublicHolidays).filter(
        PublicHolidays.holiday_date == holiday_date,
        PublicHolidays.country_code == country_code,
        PublicHolidays.region == region
    )

    if exclude_holiday_id is not None:
        query = query.filter(
            PublicHolidays.public_holiday_id != exclude_holiday_id
        )

    return query.first()


def create_public_holiday_record(
    db: Session,
    holiday_data: dict
):
    holiday = PublicHolidays(**holiday_data)

    try:
        db.add(holiday)
        db.commit()
        db.refresh(holiday)
        return holiday

    except Exception:
        db.rollback()
        raise


def update_public_holiday_record(
    db: Session,
    holiday: PublicHolidays,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(holiday, key, value)

        db.commit()
        db.refresh(holiday)
        return holiday

    except Exception:
        db.rollback()
        raise