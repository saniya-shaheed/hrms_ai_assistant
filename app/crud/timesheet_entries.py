from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.timesheet_entries import TimesheetEntries


def get_hours_for_work_date(
    db: Session,
    timesheet_id: int,
    work_date
):
    return (
        db.query(
            func.coalesce(
                func.sum(TimesheetEntries.hours_worked),
                0
            )
        )
        .filter(
            TimesheetEntries.timesheet_id == timesheet_id,
            TimesheetEntries.work_date == work_date
        )
        .scalar()
    )


def get_total_entry_hours(
    db: Session,
    timesheet_id: int
):
    return (
        db.query(
            func.coalesce(
                func.sum(TimesheetEntries.hours_worked),
                0
            )
        )
        .filter(
            TimesheetEntries.timesheet_id == timesheet_id
        )
        .scalar()
    )


def create_timesheet_entry_record(
    db: Session,
    timesheet,
    entry_data: dict
):
    entry = TimesheetEntries(
        timesheet_id=timesheet.timesheet_id,
        **entry_data
    )

    try:
        db.add(entry)
        db.flush()

        # Recalculate total hours from actual entries.
        total_hours = get_total_entry_hours(
            db,
            timesheet.timesheet_id
        )

        timesheet.total_hours = total_hours

        db.commit()

        db.refresh(entry)
        db.refresh(timesheet)

        return entry

    except Exception:
        db.rollback()
        raise