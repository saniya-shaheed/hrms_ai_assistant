from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.employees import get_employee_by_id


def get_my_employee_details(db: Session, current_user):

    employee_id = current_user.employee_id

    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile is linked to this user."
        )

    employee = get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee details not found."
        )

    return {
        "employee_code": employee.employee_code,
        "employee_name": employee.employee_name,
        "email": employee.email,
        "department_id": employee.department_id,
        "job_title": employee.job_title,
        "hire_date": (
            employee.hire_date.isoformat()
            if employee.hire_date else None
        )
    }