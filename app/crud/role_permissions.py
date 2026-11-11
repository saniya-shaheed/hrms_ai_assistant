from sqlalchemy.orm import Session

from app.models.role_permissions import RolePermissions


def get_role_permission_assignment(
    db: Session,
    role_id: int,
    permission_id: int
):
    return (
        db.query(RolePermissions)
        .filter(
            RolePermissions.role_id == role_id,
            RolePermissions.permission_id == permission_id
        )
        .first()
    )


def create_role_permission_assignment(
    db: Session,
    role_id: int,
    permission_id: int
):
    assignment = RolePermissions(
        role_id=role_id,
        permission_id=permission_id
    )

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    except Exception:
        db.rollback()
        raise