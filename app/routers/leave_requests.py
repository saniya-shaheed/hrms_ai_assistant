from datetime import date, timedelta

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

from app.dependencies.authorization import (
    require_permission
)

from app.crud.leave_requests import (
    get_leave_request_by_id,
    get_employee_leave_requests,
    get_overlapping_leave_request,
    get_leave_balance_for_year,
    get_pending_leave_days,
    create_leave_request_record
)

from app.crud.leave_types import get_leave_type_by_code
from app.crud.employees import get_employee_by_id
from app.crud.users import get_user_permissions

from app.schema.leave_requests import (
    LeaveRequestsCreate,
    LeaveRequestsOut
)


router = APIRouter(
    prefix="/leave/requests",
    tags=["Leave Requests"]
)


# --------------------------------------------------
# 1. CREATE LEAVE REQUEST
# POST /leave/requests
# --------------------------------------------------

@router.post(
    "",
    response_model=LeaveRequestsOut,
    status_code=status.HTTP_201_CREATED
)
def create_leave_request(
    request_data: LeaveRequestsCreate,
    current_user=Depends(
        require_permission("leave.create")
    ),
    db: Session = Depends(get_db)
):

    employee_id = current_user.employee_id

    # Retrieve the employee linked to the logged-in user
    employee = get_employee_by_id(db, employee_id)

    if employee is None or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee profile is inactive or unavailable"
        )

    # Retrieve leave type
    leave_type = get_leave_type_by_code(
        db,
        request_data.leave_type_code
    )

    if leave_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    if not leave_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This leave type is inactive"
        )

    # Calculate inclusive calendar days
    days_requested = (
        request_data.end_date - request_data.start_date
    ).days + 1

    # Check minimum notice period
    earliest_allowed_date = (
        date.today()
        + timedelta(
            days=leave_type.min_notice_calender_days
        )
    )

    if request_data.start_date < earliest_allowed_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Leave request does not meet the minimum notice period. "
                f"Earliest allowed start date is {earliest_allowed_date}"
            )
        )

    # Check maximum consecutive days
    if (
        leave_type.max_consecutive_days is not None
        and days_requested > leave_type.max_consecutive_days
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested leave exceeds the maximum consecutive days"
        )

    # Check overlapping Pending or Approved requests
    overlapping_request = get_overlapping_leave_request(
        db,
        employee_id,
        request_data.start_date,
        request_data.end_date
    )

    if overlapping_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An existing pending or approved leave request overlaps these dates"
        )

    # Check leave balance for each calendar year

    if leave_type.is_paid:
        first_year = request_data.start_date.year
        last_year = request_data.end_date.year
        
        for year in range(first_year, last_year + 1):

            period_start = max(
                request_data.start_date,
                date(year, 1, 1)
            )

            period_end = min(
                request_data.end_date,
                date(year, 12, 31)
            )

            days_for_year = (
                period_end - period_start
            ).days + 1

            balance = get_leave_balance_for_year(
                db,
                employee_id,
                request_data.leave_type_code,
                year
            )

            if balance is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No leave balance found for {year}"
                )

            available_days = (
                balance.entitlement_days - balance.used_days
            )

            pending_days = get_pending_leave_days(
                db,
                employee_id,
                request_data.leave_type_code,
                period_start,
                period_end
            )

            remaining_days = available_days - pending_days

            if days_for_year > remaining_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient leave balance for {year}. "
                        f"Available after pending requests: {remaining_days} days. "
                        f"Requested: {days_for_year} days."
                    )
                )

    # Create the request with server-controlled values
    new_request = {
        "employee_id": employee_id,
        "leave_type_code": request_data.leave_type_code,
        "start_date": request_data.start_date,
        "end_date": request_data.end_date,
        "days_requested": days_requested,
        "reason": request_data.reason,
        "status": "Pending"
    }

    try:
        return create_leave_request_record(
            db,
            new_request
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave request conflicts with existing records"
        )


# --------------------------------------------------
# 2. GET OWN LEAVE REQUESTS
# GET /leave/requests/me
# --------------------------------------------------

@router.get(
    "/me",
    response_model=list[LeaveRequestsOut]
)
def get_my_leave_requests(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    return get_employee_leave_requests(
        db,
        current_user.employee_id,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 3. GET LEAVE REQUEST BY ID
# GET /leave/requests/{request_id}
# --------------------------------------------------

@router.get(
    "/{request_id}",
    response_model=LeaveRequestsOut
)
def get_leave_request_details(
    request_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    leave_request = get_leave_request_by_id(
        db,
        request_id
    )

    if leave_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Owner can view their own request
    if current_user.employee_id == leave_request.employee_id:
        return leave_request

    # Retrieve permissions
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR / Administrator can view all requests
    if "leave.request.read_all" in permission_codes:
        return leave_request

    # Manager can view requests from assigned direct reports
    if "leave.request.read_team" in permission_codes:

        employee = get_employee_by_id(
            db,
            leave_request.employee_id
        )

        if (
            employee is not None
            and employee.manager_employee_id == current_user.employee_id
        ):
            return leave_request

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this leave request"
    )