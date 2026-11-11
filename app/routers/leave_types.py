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

from app.crud.leave_types import (
    get_all_active_leave_types,
    get_leave_type_by_id,
    get_leave_type_by_code,
    create_leave_type_record,
    update_leave_type_record
)

from app.schema.leave_types import (
    LeaveTypesCreate,
    LeaveTypesUpdate,
    LeaveTypesOut
)


router = APIRouter(
    prefix="/leave/types",
    tags=["Leave Types"]
)


# --------------------------------------------------
# 1. GET ALL ACTIVE LEAVE TYPES
# GET /leave/types
# --------------------------------------------------

@router.get(
    "",
    response_model=list[LeaveTypesOut]
)
def list_leave_types(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return get_all_active_leave_types(
        db,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 2. CREATE LEAVE TYPE
# POST /leave/types
# --------------------------------------------------

@router.post(
    "",
    response_model=LeaveTypesOut,
    status_code=status.HTTP_201_CREATED
)
def create_leave_type(
    leave_type_data: LeaveTypesCreate,
    current_user=Depends(
        require_permission("leave.type.create")
    ),
    db: Session = Depends(get_db)
):

    # Check duplicate leave type code
    existing_leave_type = get_leave_type_by_code(
        db,
        leave_type_data.leave_type_code
    )

    if existing_leave_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave type code already exists"
        )

    try:
        return create_leave_type_record(
            db,
            leave_type_data.model_dump()
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave type conflicts with existing records"
        )


# --------------------------------------------------
# 3. UPDATE LEAVE TYPE
# PATCH /leave/types/{leave_type_id}
# --------------------------------------------------

@router.patch(
    "/{leave_type_id}",
    response_model=LeaveTypesOut
)
def update_leave_type(
    leave_type_id: int,
    leave_type_data: LeaveTypesUpdate,
    current_user=Depends(
        require_permission("leave.type.update")
    ),
    db: Session = Depends(get_db)
):

    # Find leave type
    leave_type = get_leave_type_by_id(
        db,
        leave_type_id
    )

    if leave_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    # Retrieve only the supplied fields
    update_data = leave_type_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Required fields cannot be NULL
    required_fields = [
        "leave_type_code",
        "leave_type_name",
        "is_paid",
        "requires_approval",
        "min_notice_calender_days",
        "is_active"
    ]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    # Check duplicate leave type code
    if update_data.get("leave_type_code") is not None:

        existing_leave_type = get_leave_type_by_code(
            db,
            update_data["leave_type_code"],
            exclude_leave_type_id=leave_type_id
        )

        if existing_leave_type:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Leave type code already exists"
            )

    try:
        return update_leave_type_record(
            db,
            leave_type,
            update_data
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave type update conflicts with existing records"
        )