from sqlalchemy.orm import Session

from app.models.employees import Employees
from app.models.permissions import Permissions
from app.models.roles import Roles
from app.models.users import Users
from app.models.user_roles import UserRoles
from app.models.role_permissions import RolePermissions


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

def get_user_roles(db: Session, user_id: int):
    return (
        db.query(Roles)
        .join(UserRoles, UserRoles.role_id == Roles.role_id)
        .filter(UserRoles.user_id == user_id)
        .all()
    )

def get_user_permissions(db: Session, user_id: int):
    return (
        db.query(Permissions)
        .join(
            RolePermissions,
            RolePermissions.permission_id == Permissions.permission_id
        )
        .join(
            UserRoles,
            UserRoles.role_id == RolePermissions.role_id
        )
        .filter(UserRoles.user_id == user_id)
        .distinct()
        .order_by(Permissions.permission_code)
        .all()
    )

def get_user_by_employee_id(db: Session, employee_id: int):
    return (
        db.query(Users)
        .filter(Users.employee_id == employee_id)
        .first()
    )


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(Users)
        .order_by(Users.user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user_record(db: Session, user_data: dict):
    user = Users(**user_data)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except Exception:
        db.rollback()
        raise


def update_user_record(
    db: Session,
    user: Users,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    except Exception:
        db.rollback()
        raise


def update_user_password(
    db: Session,
    user: Users,
    password_hash: str
):
    try:
        user.password_hash = password_hash

        db.commit()
        db.refresh(user)
        return user

    except Exception:
        db.rollback()
        raise