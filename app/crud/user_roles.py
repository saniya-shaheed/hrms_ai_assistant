from sqlalchemy.orm import Session

from app.models.user_roles import UserRoles


def get_user_role_assignment(
    db: Session,
    user_id: int,
    role_id: int
):
    return (
        db.query(UserRoles)
        .filter(
            UserRoles.user_id == user_id,
            UserRoles.role_id == role_id
        )
        .first()
    )


def create_user_role_assignment(
    db: Session,
    user_id: int,
    role_id: int
):
    assignment = UserRoles(
        user_id=user_id,
        role_id=role_id
    )

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    except Exception:
        db.rollback()
        raise