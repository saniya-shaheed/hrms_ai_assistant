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