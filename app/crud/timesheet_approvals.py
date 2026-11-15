from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.timesheet_approvals import TimesheetApprovals


def create_timesheet_approval_record(
    db: Session,
    timesheet,
    approver_employee_id: int,
    decision: str,
    comments: str | None
):
    approval = TimesheetApprovals(
        timesheet_id=timesheet.timesheet_id,
        approver_employee_id=approver_employee_id,
        decision=decision,
        comments=comments
    )

    try:
        db.add(approval)

        # Update the timesheet status.
        timesheet.status = decision.lower()
        timesheet.reviewer_comments = comments

        if decision == "Approved":
            timesheet.approved_at = func.now()
        else:
            timesheet.approved_at = None

        db.commit()

        db.refresh(approval)
        db.refresh(timesheet)

        return approval

    except Exception:
        db.rollback()
        raise