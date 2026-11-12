from datetime import date

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

from app.crud.users import get_user_permissions
from app.crud.leave_approvals import (
    get_leave_request_for_update,
    get_pending_leave_requests
)

from app.crud.leave_requests import (
    get_leave_balance_for_year,
    get_pending_leave_days
)

from app.models.leave_approvals import LeaveApprovals
from app.models.leave_types import LeaveTypes
from app.models.leave_transactions import LeaveTransactions

from app.schema.leave_requests import LeaveRequestsOut
from app.schema.leave_approvals import (
    LeaveDecisionRequest,
    LeaveApprovalsOut
)

pending_router = APIRouter(
    prefix="/leave/approvals",
    tags=["Leave Approvals"]
)

decision_router = APIRouter(
    prefix="/leave/requests",
    tags=["Leave Approvals"]
)

# --------------------------------------------------
# 1. GET PENDING APPROVALS
# GET /leave/approvals/pending
# --------------------------------------------------

@pending_router.get(
    "/pending",
    response_model=list[LeaveRequestsOut]
)
def get_pending_approvals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR approver: all pending requests
    if "leave.approval.read_all" in permission_codes:
        all_requests = True

    # Manager / Approver: assigned direct reports
    elif "leave.approval.read_team" in permission_codes:
        all_requests = False

        if current_user.employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not linked to an employee profile"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to view pending approvals"
        )

    return get_pending_leave_requests(
        db,
        approver_employee_id=current_user.employee_id,
        all_requests=all_requests,
        skip=skip,
        limit=limit
    )

# --------------------------------------------------
# 2. APPROVE OR REJECT A LEAVE REQUEST
# POST /leave/requests/{request_id}/decision
# --------------------------------------------------

@decision_router.post(
    "/{request_id}/decision",
    response_model=LeaveApprovalsOut
)
def decide_leave_request(
    request_id: int,
    decision_data: LeaveDecisionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Lock the request so it cannot be decided twice concurrently.
    leave_request = get_leave_request_for_update(
        db,
        request_id
    )

    if leave_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Prevent employees from approving their own requests.
    if current_user.employee_id == leave_request.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve or reject your own leave request"
        )

    # Only Pending requests can be decided.
    if leave_request.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This leave request has already been {leave_request.status.lower()}"
        )

    # Retrieve approver permissions.
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # Verify whether the user is authorised for this request.
    if "leave.approval.decide_all" in permission_codes:
        pass

    elif "leave.approval.decide_team" in permission_codes:

        from app.crud.employees import get_employee_by_id

        employee = get_employee_by_id(
            db,
            leave_request.employee_id
        )

        if (
            employee is None
            or employee.manager_employee_id != current_user.employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the assigned manager for this employee"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to decide this leave request"
        )

    # Retrieve the relevant leave type.
    leave_type = (
        db.query(LeaveTypes)
        .filter(
            LeaveTypes.leave_type_code ==
            leave_request.leave_type_code
        )
        .first()
    )

    if leave_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    decision = decision_data.decision
    transactions = []

    try:

        # ------------------------------------------
        # APPROVAL: update leave balances if paid
        # ------------------------------------------

        if decision == "Approved" and leave_type.is_paid:

            first_year = leave_request.start_date.year
            last_year = leave_request.end_date.year

            balances_to_update = []

            for year in range(first_year, last_year + 1):

                period_start = max(
                    leave_request.start_date,
                    date(year, 1, 1)
                )

                period_end = min(
                    leave_request.end_date,
                    date(year, 12, 31)
                )

                days_for_year = (
                    period_end - period_start
                ).days + 1

                # Lock the employee's balance for this year.
                balance = get_leave_balance_for_year(
                    db,
                    leave_request.employee_id,
                    leave_request.leave_type_code,
                    year,
                    for_update=True
                )

                if balance is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No leave balance found for {year}"
                    )

                # Exclude the current request from pending reservations.
                other_pending_days = get_pending_leave_days(
                    db,
                    leave_request.employee_id,
                    leave_request.leave_type_code,
                    period_start,
                    period_end,
                    exclude_request_id=leave_request.leave_request_id
                )

                available_days = (
                    balance.entitlement_days
                    - balance.used_days
                    - other_pending_days
                )

                if days_for_year > available_days:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Insufficient leave balance for {year}. "
                            f"Available after other pending requests: "
                            f"{available_days} days."
                        )
                    )

                balances_to_update.append(
                    (balance, days_for_year)
                )

            # All years have passed validation.
            # Now update balances and create transaction records.
            for balance, days_for_year in balances_to_update:

                balance.used_days += days_for_year

                transaction = LeaveTransactions(
                    employee_id=leave_request.employee_id,
                    leave_balance_id=balance.leave_balance_id,
                    leave_request_id=leave_request.leave_request_id,
                    transaction_type="LEAVE_USED",
                    days_delta=-days_for_year,
                    notes=(
                        f"Approved leave request "
                        f"#{leave_request.leave_request_id}"
                    ),
                    actor_user_id=current_user.user_id
                )

                db.add(transaction)
                transactions.append(transaction)

        # ------------------------------------------
        # UPDATE REQUEST STATUS
        # ------------------------------------------

        leave_request.status = decision

        # ------------------------------------------
        # CREATE APPROVAL HISTORY
        # ------------------------------------------

        approval = LeaveApprovals(
            leave_request_id=leave_request.leave_request_id,
            approver_employee_id=current_user.employee_id,
            decision=decision,
            comments=decision_data.comments
        )

        db.add(approval)

        # Commit request, balances, transactions and approval together.
        db.commit()

        db.refresh(approval)

        return approval

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave approval conflicts with existing records"
        )

    except Exception:
        db.rollback()
        raise