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

from app.crud.leave_balances import (
    get_balances_by_employee,
    get_balance_by_id,
    adjust_leave_balance
)

from app.crud.employees import get_employee_by_id
from app.crud.users import get_user_permissions

from app.schema.leave_balances_trasactions import (
    LeaveBalancesOut,
    LeaveBalanceAdjustment,
    LeaveBalanceAdjustmentOut
)


router = APIRouter(
    prefix="/leave/balances",
    tags=["Leave Balances"]
)


# --------------------------------------------------
# 1. GET OWN LEAVE BALANCES
# GET /leave/balances/me
# --------------------------------------------------

@router.get(
    "/me",
    response_model=list[LeaveBalancesOut]
)
def get_my_leave_balances(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    balance_year: int | None = Query(default=None, ge=2000, le=2100)
):
    return get_balances_by_employee(
        db,
        current_user.employee_id,
        balance_year=balance_year
    )


# --------------------------------------------------
# 2. GET AN EMPLOYEE'S LEAVE BALANCES # hr, manager
# GET /leave/balances/employee/{employee_id}
# --------------------------------------------------

@router.get(
    "/employee/{employee_id}",
    response_model=list[LeaveBalancesOut]
)
def get_employee_leave_balances(
    employee_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    balance_year: int | None = Query(default=None, ge=2000, le=2100)
):
    # Check whether employee exists
    employee = get_employee_by_id(
        db,
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Retrieve current user's permissions
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR: Can view all employee balances
    if "leave.balance.read_all" in permission_codes:
        pass

    # Manager: Can view direct reports' balances
    elif (
        "leave.balance.read_team" in permission_codes
        and employee.manager_employee_id == current_user.employee_id
    ):
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this employee's leave balances"
        )

    return get_balances_by_employee(
        db,
        employee_id,
        balance_year=balance_year
    )


# --------------------------------------------------
# 3. ADJUST LEAVE BALANCE #admin
# PATCH /leave/balances/{balance_id}
# --------------------------------------------------

@router.patch(
    "/{balance_id}",
    response_model=LeaveBalanceAdjustmentOut
)
def update_leave_balance(
    balance_id: int,
    adjustment_data: LeaveBalanceAdjustment,
    current_user=Depends(
        require_permission("leave.balance.adjust")
    ),
    db: Session = Depends(get_db)
):

    # Find the balance record
    balance = get_balance_by_id(
        db,
        balance_id
    )

    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave balance not found"
        )

    try:
        updated_balance, transaction = adjust_leave_balance(
            db=db,
            balance=balance,
            days_delta=adjustment_data.days_delta,
            reason=adjustment_data.reason,
            actor_user_id=current_user.user_id
        )

        return {
            "balance": updated_balance,
            "transaction": transaction
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave balance adjustment conflicts with existing records"
        )