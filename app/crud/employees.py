from sqlalchemy.orm import Session

from app.models.employees import Employees


def get_employee_by_id(db: Session, employee_id: int):
    return (
        db.query(Employees)
        .filter(Employees.employee_id == employee_id)
        .first()
    )

def get_all_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    manager_employee_id: int | None = None
):
    query = db.query(Employees)

    if manager_employee_id is not None:
        query = query.filter(
            Employees.manager_employee_id == manager_employee_id
        )

    return (
        query
        .order_by(Employees.employee_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_employee_by_email(db: Session, email: str):
    return (
        db.query(Employees)
        .filter(Employees.email == email)
        .first()
    )


def get_employee_by_code(db: Session, employee_code: str):
    return (
        db.query(Employees)
        .filter(Employees.employee_code == employee_code)
        .first()
    )


def create_employee_record(db: Session, employee_data: dict):
    employee = Employees(**employee_data)

    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    except Exception:
        db.rollback()
        raise


def update_employee_record(
    db: Session,
    employee: Employees,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(employee, key, value)

        db.commit()
        db.refresh(employee)
        return employee

    except Exception:
        db.rollback()
        raise