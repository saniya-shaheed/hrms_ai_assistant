from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from datetime import date

from app.models.leave_requests import LeaveRequests
from app.models.leave_approvals import LeaveApprovals
from app.models.leave_transactions import LeaveTransactions
from app.models.leave_types import LeaveTypes

from app.crud.leave_approvals import (
    get_leave_request_for_update,
)

from app.crud.employees import get_employee_by_id

from app.crud.leave_requests import (
    get_leave_balance_for_year,
    get_pending_leave_days,
)

from app.crud.leave_types import (
    get_leave_type_by_code,
)

from app.crud.users import (
    get_user_permissions,
)

from app.core.leave_calender import (
    get_working_days,
)

def decide_leave_request_service(
    db: Session,
    current_user,
    request_id: int,
    decision: str,
    remarks: str | None = None
):
    if decision not in ("Approved", "Rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be Approved or Rejected"
        )
    # ------------------------------------------
    # 1. Retrieve and lock leave request
    # ------------------------------------------

    leave_request = get_leave_request_for_update(
        db,
        request_id
    )

    if leave_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # ------------------------------------------
    # 2. Prevent self-approval
    # ------------------------------------------

    if current_user.employee_id == leave_request.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve or reject your own leave request"
        )

    # ------------------------------------------
    # 3. Only Pending requests can be decided
    # ------------------------------------------

    if leave_request.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"This leave request has already been "
                f"{leave_request.status.lower()}"
            )
        )

    # ------------------------------------------
    # 4. Validate approver permissions
    # ------------------------------------------

    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # ------------------------------------------
    # 5. Check approval scope
    # ------------------------------------------

    if "leave.approval.decide_all" in permission_codes:

        # HR-level approver
        pass

    elif "leave.approval.decide_team" in permission_codes:

        if current_user.employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not linked to an employee profile"
            )

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

    # ------------------------------------------
    # 6. Retrieve leave type
    # ------------------------------------------

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

    # transactions = []

    try:

        # ======================================
        # 7. APPROVAL PROCESSING
        # ======================================

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

                days_for_year = get_working_days(
                    db,
                    period_start,
                    period_end
                )

                if days_for_year == 0:
                    continue

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

                other_pending_days = get_pending_leave_days(
                    db,
                    leave_request.employee_id,
                    leave_request.leave_type_code,
                    date(year, 1, 1),
                    date(year, 12, 31),
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

            # ----------------------------------
            # Update balances
            # ----------------------------------

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
                # transactions.append(transaction)

        # ======================================
        # 8. UPDATE REQUEST STATUS
        # ======================================

        leave_request.status = decision

        # ======================================
        # 9. CREATE APPROVAL HISTORY
        # ======================================

        approval = LeaveApprovals(
            leave_request_id=leave_request.leave_request_id,
            approver_employee_id=current_user.employee_id,
            decision=decision,
            comments=remarks
        )

        db.add(approval)

        # ======================================
        # 10. COMMIT EVERYTHING
        # ======================================

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

def decide_leave_request_from_ai(
    db: Session,
    current_user,
    request_id: int,
    decision: str,
    remarks: str | None = None
):
    approval = decide_leave_request_service(
        db=db,
        current_user=current_user,
        request_id=request_id,
        decision=decision,
        remarks=remarks
    )

    return {
        "success": True,
        "message": f"Leave request #{request_id} has been {decision.lower()}",
        "request_id": request_id,
        "decision": decision,
        "remarks": remarks
    }