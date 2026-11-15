from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from app.models.timesheet_entries import TimesheetEntries
from app.models.timesheets import Timesheets


def get_timesheet_by_id(
    db: Session,
    timesheet_id: int,
    for_update: bool = False
):
    query = (
        db.query(Timesheets)
        .options(selectinload(Timesheets.timesheet_entries))
        .filter(Timesheets.timesheet_id == timesheet_id)
    )

    if for_update:
        query = query.with_for_update()

    return query.first()


def get_employee_timesheets(
    db: Session,
    employee_id: int,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(Timesheets)
        .options(selectinload(Timesheets.timesheet_entries))
        .filter(Timesheets.employee_id == employee_id)
        .order_by(Timesheets.period_start.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_overlapping_timesheet(
    db: Session,
    employee_id: int,
    period_start,
    period_end
):
    return (
        db.query(Timesheets)
        .filter(
            Timesheets.employee_id == employee_id,
            Timesheets.status.notin_(["rejected", "Rejected"]),
            Timesheets.period_start <= period_end,
            Timesheets.period_end >= period_start
        )
        .first()
    )


def create_timesheet_record(
    db: Session,
    timesheet_data: dict
):
    timesheet = Timesheets(**timesheet_data)

    try:
        db.add(timesheet)
        db.commit()
        db.refresh(timesheet)
        return timesheet

    except Exception:
        db.rollback()
        raise


