from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.authorization import require_permission

from app.crud.public_holidays import (
    get_all_public_holidays,
    get_public_holiday_by_id,
    get_duplicate_public_holiday,
    create_public_holiday_record,
    update_public_holiday_record
)

from app.schema.public_holidays import (
    PublicHolidaysCreate,
    PublicHolidaysUpdate,
    PublicHolidaysOut
)


router = APIRouter(
    prefix="/holidays",
    tags=["Public Holidays"]
)


# --------------------------------------------------
# 1. GET ALL ACTIVE PUBLIC HOLIDAYS
# GET /holidays
# --------------------------------------------------

@router.get(
    "",
    response_model=list[PublicHolidaysOut]
)
def list_public_holidays(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    year: int | None = Query(default=None, ge=2000, le=2100),
    country_code: str | None = Query(default=None, min_length=2),
    region: str | None = Query(default=None)
):
    return get_all_public_holidays(
        db,
        skip=skip,
        limit=limit,
        year=year,
        country_code=country_code,
        region=region
    )


# --------------------------------------------------
# 2. CREATE PUBLIC HOLIDAY
# POST /holidays
# --------------------------------------------------

@router.post(
    "",
    response_model=PublicHolidaysOut,
    status_code=status.HTTP_201_CREATED
)
def create_public_holiday(
    holiday_data: PublicHolidaysCreate,
    current_user=Depends(
        require_permission("holiday.create")
    ),
    db: Session = Depends(get_db)
):

    existing_holiday = get_duplicate_public_holiday(
        db,
        holiday_data.holiday_date,
        holiday_data.country_code,
        holiday_data.region
    )

    if existing_holiday:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A public holiday already exists for this date, country and region"
        )

    holiday_record = holiday_data.model_dump()

    try:
        return create_public_holiday_record(
            db,
            holiday_record
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Public holiday conflicts with existing records"
        )


# --------------------------------------------------
# 3. UPDATE PUBLIC HOLIDAY
# PATCH /holidays/{holiday_id}
# --------------------------------------------------

@router.patch(
    "/{holiday_id}",
    response_model=PublicHolidaysOut
)
def update_public_holiday(
    holiday_id: int,
    holiday_data: PublicHolidaysUpdate,
    current_user=Depends(
        require_permission("holiday.update")
    ),
    db: Session = Depends(get_db)
):

    # Find existing holiday
    holiday = get_public_holiday_by_id(
        db,
        holiday_id
    )

    if holiday is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public holiday not found"
        )

    # Get only fields supplied in the request
    update_data = holiday_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Required fields cannot be NULL
    required_fields = [
        "holiday_date",
        "holiday_name",
        "country_code",
        "region",
        "is_active"
    ]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    # Determine the final values after the update
    final_date = update_data.get(
        "holiday_date",
        holiday.holiday_date
    )

    final_country = update_data.get(
        "country_code",
        holiday.country_code
    )

    final_region = update_data.get(
        "region",
        holiday.region
    )

    # Check duplicate date/country/region combination
    duplicate = get_duplicate_public_holiday(
        db,
        final_date,
        final_country,
        final_region,
        exclude_holiday_id=holiday_id
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another public holiday already exists for this date, country and region"
        )

    try:
        return update_public_holiday_record(
            db,
            holiday,
            update_data
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Public holiday update conflicts with existing records"
        )