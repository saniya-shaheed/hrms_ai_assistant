from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.leave_balances import get_balances_by_employee


def get_my_leave_balance(
    db: Session,
    current_user,
    balance_year: int | None = None
):
    employee_id = current_user.employee_id

    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile is linked to this user."
        )

    balances = get_balances_by_employee(
        db=db,
        employee_id=employee_id,
        balance_year=balance_year
    )

    return [
        {
            "leave_type_code": balance.leave_type_code,
            "entitlement_days": balance.entitlement_days,
            "used_days": balance.used_days,
            "available_days": balance.available_days,
            "balance_year": balance.balance_year
        }
        for balance in balances
    ]