from sqlalchemy.orm import Session

from app.models.permissions import Permissions


def get_all_permissions(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(Permissions)
        .order_by(Permissions.permission_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_permission_by_id(db: Session, permission_id: int):
    return (
        db.query(Permissions)
        .filter(Permissions.permission_id == permission_id)
        .first()
    )