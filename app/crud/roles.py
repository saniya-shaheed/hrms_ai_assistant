from sqlalchemy.orm import Session

from app.models.roles import Roles


def get_all_roles(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Roles)
        .order_by(Roles.role_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_role_by_id(db: Session, role_id: int):
    return (
        db.query(Roles)
        .filter(Roles.role_id == role_id)
        .first()
    )


def get_role_by_name(
    db: Session,
    role_name: str,
    exclude_role_id: int | None = None
):
    query = db.query(Roles).filter(
        Roles.role_name == role_name
    )

    if exclude_role_id is not None:
        query = query.filter(Roles.role_id != exclude_role_id)

    return query.first()


def create_role_record(db: Session, role_data: dict):
    role = Roles(**role_data)

    try:
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    except Exception:
        db.rollback()
        raise


def update_role_record(
    db: Session,
    role: Roles,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(role, key, value)

        db.commit()
        db.refresh(role)
        return role

    except Exception:
        db.rollback()
        raise