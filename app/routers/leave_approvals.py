from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.leave_calender import get_working_days
from app.database import get_db

from app.dependencies.auth import get_current_user

from app.crud.users import get_user_permissions
from app.crud.leave_approvals import (
    get_leave_request_for_update,
    get_pending_leave_requests
)

from app.crud.leave_requests import (
    get_leave_balance_for_year,
    get_pending_leave_days
)

from app.models.leave_approvals import LeaveApprovals
from app.models.leave_types import LeaveTypes
from app.models.leave_transactions import LeaveTransactions

from app.schema.leave_requests import LeaveRequestsOut
from app.schema.leave_approvals import (
    LeaveDecisionRequest,
    LeaveApprovalsOut
)
from app.services.leave_approval_service import decide_leave_request_service

pending_router = APIRouter(
    prefix="/leave/approvals",
    tags=["Leave Approvals"]
)

decision_router = APIRouter(
    prefix="/leave/requests",
    tags=["Leave Approvals"]
)

# --------------------------------------------------
# 1. GET PENDING APPROVALS
# GET /leave/approvals/pending
# --------------------------------------------------

@pending_router.get(
    "/pending",
    response_model=list[LeaveRequestsOut]
)
def get_pending_approvals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR approver: all pending requests
    if "leave.approval.read_all" in permission_codes:
        all_requests = True

    # Manager / Approver: assigned direct reports
    elif "leave.approval.read_team" in permission_codes:
        all_requests = False

        if current_user.employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not linked to an employee profile"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to view pending approvals"
        )

    return get_pending_leave_requests(
        db,
        approver_employee_id=current_user.employee_id,
        all_requests=all_requests,
        skip=skip,
        limit=limit
    )

# --------------------------------------------------
# 2. APPROVE OR REJECT A LEAVE REQUEST
# POST /leave/requests/{request_id}/decision
# --------------------------------------------------

@decision_router.post(
    "/{request_id}/decision",
    response_model=LeaveApprovalsOut
)
def decide_leave_request(
    request_id: int,
    decision_data: LeaveDecisionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return decide_leave_request_service(
        db=db,
        current_user=current_user,
        request_id=request_id,
        decision=decision_data.decision,
        remarks=decision_data.comments
    )