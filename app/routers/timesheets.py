from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.database import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.authorization import require_permission

from app.crud.timesheets import (
    get_timesheet_by_id,
    get_employee_timesheets,
    get_overlapping_timesheet,
    create_timesheet_record
)

from app.crud.timesheet_entries import (
    get_hours_for_work_date,
    get_total_entry_hours,
    create_timesheet_entry_record
)

from app.crud.timesheet_approvals import (
    create_timesheet_approval_record
)

from app.crud.employees import get_employee_by_id
from app.crud.users import get_user_permissions

from app.models.timesheets import Timesheets

from app.schema.timesheets import (
    TimesheetCreate,
    TimesheetOut
)

from app.schema.timesheet_entries import (
    TimesheetEntryCreate,
    TimesheetEntryOut
)

from app.schema.timesheet_approvals import (
    TimesheetDecisionRequest,
    TimesheetApprovalOut
)


router = APIRouter(
    prefix="/timesheets",
    tags=["Timesheets"]
)


# --------------------------------------------------
# 1. CREATE WEEKLY TIMESHEET
# POST /timesheets
# --------------------------------------------------

@router.post(
    "",
    response_model=TimesheetOut,
    status_code=status.HTTP_201_CREATED
)
def create_timesheet(
    timesheet_data: TimesheetCreate,
    current_user=Depends(
        require_permission("timesheet.submit")
    ),
    db: Session = Depends(get_db)
):

    employee_id = current_user.employee_id

    # Check employee
    employee = get_employee_by_id(
        db,
        employee_id
    )

    if employee is None or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee profile is inactive or unavailable"
        )

    # Prevent overlapping timesheets for the same employee.
    existing_timesheet = get_overlapping_timesheet(
        db,
        employee_id,
        timesheet_data.period_start,
        timesheet_data.period_end
    )

    if existing_timesheet:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An overlapping timesheet already exists for this period"
        )

    timesheet_record = {
        "employee_id": employee_id,
        "period_start": timesheet_data.period_start,
        "period_end": timesheet_data.period_end,
        "status": "draft",
        "total_hours": 0,
        "employee_comments": timesheet_data.employee_comments
    }

    try:
        return create_timesheet_record(
            db,
            timesheet_record
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Timesheet conflicts with existing records"
        )


# --------------------------------------------------
# 2. GET OWN TIMESHEETS
# GET /timesheets/me
# --------------------------------------------------

@router.get(
    "/me",
    response_model=list[TimesheetOut]
)
def get_my_timesheets(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    return get_employee_timesheets(
        db,
        current_user.employee_id,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 3. GET TIMESHEET BY ID
# GET /timesheets/{timesheet_id}
# --------------------------------------------------

@router.get(
    "/{timesheet_id}",
    response_model=TimesheetOut
)
def get_timesheet_details(
    timesheet_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    timesheet = get_timesheet_by_id(
        db,
        timesheet_id
    )

    if timesheet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Owner can view their own timesheet.
    if current_user.employee_id == timesheet.employee_id:
        return timesheet

    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR can view all timesheets.
    if "timesheet.read_all" in permission_codes:
        return timesheet

    # Manager can view direct reports' timesheets.
    if "timesheet.read_team" in permission_codes:

        employee = get_employee_by_id(
            db,
            timesheet.employee_id
        )

        if (
            employee is not None
            and employee.manager_employee_id == current_user.employee_id
        ):
            return timesheet

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this timesheet"
    )


# --------------------------------------------------
# 4. ADD TIMESHEET ENTRY
# POST /timesheets/{timesheet_id}/entries
# --------------------------------------------------

@router.post(
    "/{timesheet_id}/entries",
    response_model=TimesheetEntryOut,
    status_code=status.HTTP_201_CREATED
)
def add_timesheet_entry(
    timesheet_id: int,
    entry_data: TimesheetEntryCreate,
    current_user=Depends(
        require_permission("timesheet.submit")
    ),
    db: Session = Depends(get_db)
):

    # Lock the timesheet while adding an entry.
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
        for_update=True
    )

    if timesheet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Verify ownership.
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add entries to your own timesheet"
        )

    # Entries can only be added while the sheet is a draft.
    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entries can only be added to a draft timesheet"
        )

    # Work date must fall within the timesheet period.
    if not (
        timesheet.period_start
        <= entry_data.work_date
        <= timesheet.period_end
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Work date must fall within the timesheet period"
        )

    # Check daily total.
    existing_daily_hours = get_hours_for_work_date(
        db,
        timesheet_id,
        entry_data.work_date
    )

    if existing_daily_hours + entry_data.hours_worked > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total work hours for a day cannot exceed 24"
        )

    # Check weekly total.
    current_total_hours = get_total_entry_hours(
        db,
        timesheet_id
    )

    if current_total_hours + entry_data.hours_worked > 168:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total weekly hours cannot exceed 168"
        )

    try:
        return create_timesheet_entry_record(
            db,
            timesheet,
            entry_data.model_dump()
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Timesheet entry conflicts with existing records"
        )


# --------------------------------------------------
# 5. SUBMIT TIMESHEET
# POST /timesheets/{timesheet_id}/submit
# --------------------------------------------------

@router.post(
    "/{timesheet_id}/submit",
    response_model=TimesheetOut
)
def submit_timesheet(
    timesheet_id: int,
    current_user=Depends(
        require_permission("timesheet.submit")
    ),
    db: Session = Depends(get_db)
):

    # Lock the timesheet during submission.
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
        for_update=True
    )

    if timesheet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Verify ownership.
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own timesheet"
        )

    # Only draft timesheets can be submitted.
    if timesheet.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft timesheets can be submitted"
        )

    # Recalculate from the actual entries.
    total_hours = get_total_entry_hours(
        db,
        timesheet_id
    )

    if total_hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit a timesheet without work entries"
        )

    try:
        timesheet.total_hours = total_hours
        timesheet.status = "submitted"
        timesheet.submitted_at = func.now()

        db.commit()
        db.refresh(timesheet)

        return timesheet

    except Exception:
        db.rollback()
        raise


# --------------------------------------------------
# 6. MANAGER APPROVES OR REJECTS TIMESHEET
# POST /timesheets/{timesheet_id}/decision
# --------------------------------------------------

@router.post(
    "/{timesheet_id}/decision",
    response_model=TimesheetApprovalOut
)
def decide_timesheet(
    timesheet_id: int,
    decision_data: TimesheetDecisionRequest,
    current_user=Depends(
        require_permission("timesheet.approve")
    ),
    db: Session = Depends(get_db)
):

    # Lock the timesheet during the decision.
    timesheet = get_timesheet_by_id(
        db,
        timesheet_id,
        for_update=True
    )

    if timesheet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # A timesheet cannot be approved by its owner.
    if timesheet.employee_id == current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve your own timesheet"
        )

    # Only submitted timesheets can be decided.
    if timesheet.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted timesheets can be approved or rejected"
        )

    # Check the actual reporting relationship.
    employee = get_employee_by_id(
        db,
        timesheet.employee_id
    )

    if (
        employee is None
        or employee.manager_employee_id != current_user.employee_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned manager for this employee"
        )

    try:
        return create_timesheet_approval_record(
            db,
            timesheet,
            current_user.employee_id,
            decision_data.decision,
            decision_data.comments
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Timesheet decision conflicts with existing records"
        )