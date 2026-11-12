from sqlalchemy.orm import Session

from app.models.leave_requests import LeaveRequests
from app.models.employees import Employees

def get_leave_request_for_update(
    db: Session,
    request_id: int
):
    return (
        db.query(LeaveRequests)
        .filter(
            LeaveRequests.leave_request_id == request_id
        )
        .with_for_update()
        .first()
    )

def get_pending_leave_requests(
    db: Session,
    approver_employee_id: int,
    all_requests: bool = False,
    skip: int = 0,
    limit: int = 100
):
    query = (
        db.query(LeaveRequests)
        .join(
            Employees,
            Employees.employee_id == LeaveRequests.employee_id
        )
        .filter(LeaveRequests.status == "Pending")
    )

    # HR approvers can view all pending requests.
    # Managers and designated Approvers see direct reports only.
    if not all_requests:
        query = query.filter(
            Employees.manager_employee_id == approver_employee_id
        )

    return (
        query
        .order_by(LeaveRequests.submitted_at)
        .offset(skip)
        .limit(limit)
        .all()
    )