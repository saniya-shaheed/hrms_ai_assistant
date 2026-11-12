from datetime import date

from sqlalchemy.orm import Session

from app.models.leave_requests import LeaveRequests
from app.models.leave_balances import LeaveBalances


def get_leave_request_by_id(
    db: Session,
    request_id: int
):
    return (
        db.query(LeaveRequests)
        .filter(
            LeaveRequests.leave_request_id == request_id
        )
        .first()
    )


def get_employee_leave_requests(
    db: Session,
    employee_id: int,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(LeaveRequests)
        .filter(LeaveRequests.employee_id == employee_id)
        .order_by(LeaveRequests.submitted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_overlapping_leave_request(
    db: Session,
    employee_id: int,
    start_date: date,
    end_date: date
):
    return (
        db.query(LeaveRequests)
        .filter(
            LeaveRequests.employee_id == employee_id,
            LeaveRequests.status.in_(["Pending", "Approved"]),
            LeaveRequests.start_date <= end_date,
            LeaveRequests.end_date >= start_date
        )
        .first()
    )


def get_leave_balance_for_year(
    db: Session,
    employee_id: int,
    leave_type_code: str,
    balance_year: int
):
    return (
        db.query(LeaveBalances)
        .filter(
            LeaveBalances.employee_id == employee_id,
            LeaveBalances.leave_type_code == leave_type_code,
            LeaveBalances.balance_year == balance_year
        )
        .first()
    )


def get_pending_leave_days(
    db: Session,
    employee_id: int,
    leave_type_code: str,
    period_start: date,
    period_end: date
):
    pending_requests = (
        db.query(LeaveRequests)
        .filter(
            LeaveRequests.employee_id == employee_id,
            LeaveRequests.leave_type_code == leave_type_code,
            LeaveRequests.status == "Pending",
            LeaveRequests.start_date <= period_end,
            LeaveRequests.end_date >= period_start
        )
        .all()
    )

    pending_days = 0

    for request in pending_requests:
        overlap_start = max(request.start_date, period_start)
        overlap_end = min(request.end_date, period_end)

        if overlap_start <= overlap_end:
            pending_days += (
                overlap_end - overlap_start
            ).days + 1

    return pending_days


def create_leave_request_record(
    db: Session,
    request_data: dict
):
    leave_request = LeaveRequests(**request_data)

    try:
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        return leave_request

    except Exception:
        db.rollback()
        raise