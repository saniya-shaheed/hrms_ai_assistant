from sqlalchemy.orm import Session

from app.models.departments import Departments


def get_all_departments(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(Departments)
        .order_by(Departments.department_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_department_by_id(db: Session, department_id: int):
    return (
        db.query(Departments)
        .filter(Departments.department_id == department_id)
        .first()
    )


def get_department_by_name(
    db: Session,
    department_name: str,
    exclude_department_id: int | None = None
):
    query = db.query(Departments).filter(
        Departments.department_name == department_name
    )

    if exclude_department_id is not None:
        query = query.filter(
            Departments.department_id != exclude_department_id
        )

    return query.first()


def get_department_by_code(
    db: Session,
    department_code: str,
    exclude_department_id: int | None = None
):
    query = db.query(Departments).filter(
        Departments.department_code == department_code
    )

    if exclude_department_id is not None:
        query = query.filter(
            Departments.department_id != exclude_department_id
        )

    return query.first()


def create_department_record(
    db: Session,
    department_data: dict
):
    department = Departments(**department_data)

    try:
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    except Exception:
        db.rollback()
        raise


def update_department_record(
    db: Session,
    department: Departments,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(department, key, value)

        db.commit()
        db.refresh(department)
        return department

    except Exception:
        db.rollback()
        raise