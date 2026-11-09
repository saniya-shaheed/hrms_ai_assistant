from sqlalchemy.orm import Session

from app.models.employees import Employees
from app.models.users import Users


def get_user_by_email(db: Session, email: str):
    return (
        db.query(Users)
        .join(Employees, Users.employee_id == Employees.employee_id)
        .filter(Employees.email == email)
        .first()
    )

def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(Users)
        .filter(Users.user_id == user_id)
        .first()
    )