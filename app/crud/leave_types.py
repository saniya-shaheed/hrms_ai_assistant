from sqlalchemy.orm import Session

from app.models.leave_types import LeaveTypes


def get_all_active_leave_types(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(LeaveTypes)
        .filter(LeaveTypes.is_active.is_(True))
        .order_by(LeaveTypes.leave_type_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_leave_type_by_id(
    db: Session,
    leave_type_id: int
):
    return (
        db.query(LeaveTypes)
        .filter(LeaveTypes.leave_type_id == leave_type_id)
        .first()
    )


def get_leave_type_by_code(
    db: Session,
    leave_type_code: str,
    exclude_leave_type_id: int | None = None
):
    query = db.query(LeaveTypes).filter(
        LeaveTypes.leave_type_code == leave_type_code
    )

    if exclude_leave_type_id is not None:
        query = query.filter(
            LeaveTypes.leave_type_id != exclude_leave_type_id
        )

    return query.first()


def create_leave_type_record(
    db: Session,
    leave_type_data: dict
):
    leave_type = LeaveTypes(**leave_type_data)

    try:
        db.add(leave_type)
        db.commit()
        db.refresh(leave_type)
        return leave_type

    except Exception:
        db.rollback()
        raise


def update_leave_type_record(
    db: Session,
    leave_type: LeaveTypes,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(leave_type, key, value)

        db.commit()
        db.refresh(leave_type)
        return leave_type

    except Exception:
        db.rollback()
        raise