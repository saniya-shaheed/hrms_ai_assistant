from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.leave_calender import get_working_days
from app.crud.employees import get_employee_by_id
from app.crud.leave_requests import get_employee_leave_requests, get_leave_balance_for_year, get_overlapping_leave_request, get_pending_leave_days
from app.crud.leave_types import get_leave_type_by_code
from app.crud.users import get_user_permissions
from app.models.leave_requests import LeaveRequests
from app.models.leave_transactions import LeaveTransactions


def get_my_leave_requests(
    db: Session,
    current_user
):
    employee_id = current_user.employee_id

    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile is linked to this user."
        )

    leave_requests = get_employee_leave_requests(
        db=db,
        employee_id=employee_id
    )

    return [
        {
            "leave_request_id": request.leave_request_id,
            "leave_type_code": request.leave_type_code,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "days_requested": request.days_requested,
            "reason": request.reason,
            "status": request.status,
            "submitted_at": (
                request.submitted_at.isoformat()
                if request.submitted_at
                else None
            )
        }
        for request in leave_requests
    ]

def check_leave_create_permission(
    db: Session,
    current_user
):
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    if "leave.create" not in permission_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to submit a leave request."
        )

def submit_leave_request(
    db: Session,
    current_user,
    leave_type_code: str,
    start_date: date,
    end_date: date,
    reason: str | None = None
):
    employee_id = current_user.employee_id

    # ------------------------------------------
    # 1. Validate employee
    # ------------------------------------------

    employee = get_employee_by_id(
        db,
        employee_id
    )

    if employee is None or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee profile is inactive or unavailable"
        )

    # ------------------------------------------
    # 2. Validate leave type
    # ------------------------------------------

    leave_type = get_leave_type_by_code(
        db,
        leave_type_code
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

    # ------------------------------------------
    # 3. Validate date range
    # ------------------------------------------

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    # ------------------------------------------
    # 4. Calculate requested days
    # ------------------------------------------

    calendar_days = (
        end_date - start_date
    ).days + 1

    days_requested = get_working_days(
        db,
        start_date,
        end_date
    )

    if days_requested == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected period contains no working days"
        )

    # ------------------------------------------
    # 5. Validate notice period
    # ------------------------------------------

    earliest_allowed_date = (
        date.today()
        + timedelta(
            days=leave_type.min_notice_calender_days
        )
    )

    if start_date < earliest_allowed_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Leave request does not meet the minimum notice period. "
                f"Earliest allowed start date is {earliest_allowed_date}"
            )
        )

    # ------------------------------------------
    # 6. Validate maximum consecutive days
    # ------------------------------------------

    if (
        leave_type.max_consecutive_days is not None
        and calendar_days > leave_type.max_consecutive_days
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Requested period exceeds the maximum "
                "consecutive calendar days"
            )
        )

    # ------------------------------------------
    # 7. Check overlapping requests
    # ------------------------------------------

    overlapping_request = get_overlapping_leave_request(
        db,
        employee_id,
        start_date,
        end_date
    )

    if overlapping_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An existing pending or approved leave request "
                "overlaps these dates"
            )
        )

    # ------------------------------------------
    # 8. Validate leave balance
    # ------------------------------------------

    balances_to_update = []

    if leave_type.is_paid:

        first_year = start_date.year
        last_year = end_date.year

        for year in range(first_year, last_year + 1):

            period_start = max(
                start_date,
                date(year, 1, 1)
            )

            period_end = min(
                end_date,
                date(year, 12, 31)
            )

            days_for_year = get_working_days(
                db,
                period_start,
                period_end
            )

            if days_for_year == 0:
                continue

            balance = get_leave_balance_for_year(
                db,
                employee_id,
                leave_type_code,
                year,
                for_update=True
            )

            if balance is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No leave balance found for {year}"
                )

            pending_days = get_pending_leave_days(
                db,
                employee_id,
                leave_type_code,
                date(year, 1, 1),
                date(year, 12, 31)
            )

            available_days = (
                balance.entitlement_days
                - balance.used_days
                - pending_days
            )

            if days_for_year > available_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient leave balance for {year}. "
                        f"Available after pending requests: "
                        f"{available_days} days."
                    )
                )

            balances_to_update.append(
                (balance, days_for_year)
            )

    # ------------------------------------------
    # 9. Determine initial status
    # ------------------------------------------

    if leave_type.requires_approval:
        initial_status = "Pending"
    else:
        initial_status = "Approved"

    # ------------------------------------------
    # 10. Create leave request
    # ------------------------------------------

    new_request = LeaveRequests(
        employee_id=employee_id,
        leave_type_code=leave_type_code,
        start_date=start_date,
        end_date=end_date,
        days_requested=days_requested,
        reason=reason,
        status=initial_status
    )

    try:

        db.add(new_request)

        # Generate leave_request_id
        db.flush()

        # --------------------------------------
        # 11. Process automatic approval
        # --------------------------------------

        if (
            not leave_type.requires_approval
            and leave_type.is_paid
        ):

            for balance, days_for_year in balances_to_update:

                balance.used_days += days_for_year

                transaction = LeaveTransactions(
                    employee_id=employee_id,
                    leave_balance_id=balance.leave_balance_id,
                    leave_request_id=new_request.leave_request_id,
                    transaction_type="LEAVE_USED",
                    days_delta=-days_for_year,
                    notes=(
                        "Automatically approved because "
                        "approval is not required for this leave type."
                    ),
                    actor_user_id=current_user.user_id
                )

                db.add(transaction)

        # --------------------------------------
        # 12. Commit everything together
        # --------------------------------------

        db.commit()

        db.refresh(new_request)

        return new_request

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave request conflicts with existing records"
        )

    except Exception:

        db.rollback()

        raise

def submit_leave_request_from_ai(
    db: Session,
    current_user,
    leave_type_code: str,
    start_date: str,
    end_date: str,
    reason: str | None = None
):
    check_leave_create_permission(
        db=db,
        current_user=current_user
    )
    try:
        parsed_start_date = date.fromisoformat(start_date)
        parsed_end_date = date.fromisoformat(end_date)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dates must be provided in YYYY-MM-DD format."
        )

    new_request = submit_leave_request(
        db=db,
        current_user=current_user,
        leave_type_code=leave_type_code,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        reason=reason
    )

    return {
        "success": True,
        "message": "Leave request submitted successfully.",
        "leave_request_id": new_request.leave_request_id,
        "leave_type_code": new_request.leave_type_code,
        "start_date": new_request.start_date.isoformat(),
        "end_date": new_request.end_date.isoformat(),
        "days_requested": new_request.days_requested,
        "reason": new_request.reason,
        "status": new_request.status,
        "submitted_at": (
            new_request.submitted_at.isoformat()
            if new_request.submitted_at
            else None
        )
    }