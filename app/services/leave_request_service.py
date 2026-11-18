from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.leave_requests import get_employee_leave_requests


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