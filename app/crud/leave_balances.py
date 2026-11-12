from sqlalchemy.orm import Session

from app.models.leave_balances import LeaveBalances
from app.models.leave_transactions import LeaveTransactions


def get_balances_by_employee(
    db: Session,
    employee_id: int,
    balance_year: int | None = None
):
    query = db.query(LeaveBalances).filter(
        LeaveBalances.employee_id == employee_id
    )

    if balance_year is not None:
        query = query.filter(
            LeaveBalances.balance_year == balance_year
        )

    return (
        query
        .order_by(
            LeaveBalances.balance_year.desc(),
            LeaveBalances.leave_type_code
        )
        .all()
    )


def get_balance_by_id(
    db: Session,
    balance_id: int
):
    return (
        db.query(LeaveBalances)
        .filter(
            LeaveBalances.leave_balance_id == balance_id
        )
        .first()
    )


def adjust_leave_balance(
    db: Session,
    balance: LeaveBalances,
    days_delta: int,
    reason: str,
    actor_user_id: int
):
    new_entitlement = balance.entitlement_days + days_delta

    # Do not allow entitlement to fall below days already used
    if new_entitlement < balance.used_days:
        raise ValueError(
            "Adjustment cannot reduce entitlement below used leave days"
        )

    if new_entitlement < 0:
        raise ValueError(
            "Entitlement cannot become negative"
        )

    # Update the balance
    balance.entitlement_days = new_entitlement

    # Create a corresponding transaction record
    transaction = LeaveTransactions(
        employee_id=balance.employee_id,
        leave_balance_id=balance.leave_balance_id,
        transaction_type="ADJUSTMENT",
        days_delta=days_delta,
        notes=reason,
        actor_user_id=actor_user_id
    )

    try:
        db.add(transaction)

        # Both changes are committed together
        db.commit()

        db.refresh(balance)
        db.refresh(transaction)

        return balance, transaction

    except Exception:
        db.rollback()
        raise