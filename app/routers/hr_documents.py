from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db

from app.dependencies.auth import get_current_user
from app.dependencies.authorization import require_permission

from app.crud.hr_document_types import (
    get_active_document_types,
    get_document_type_by_code
)

from app.crud.hr_document_requests import (
    get_document_request_by_id,
    get_employee_document_requests,
    create_document_request_with_history,
    update_document_request_with_history
)

from app.crud.users import get_user_permissions
from app.crud.employees import get_employee_by_id

from app.schema.hr_document_types import (
    HRDocumentTypesOut
)

from app.schema.hr_document_requests import (
    HRDocumentRequestCreate,
    HRDocumentRequestUpdate,
    HRDocumentRequestOut
)


document_types_router = APIRouter(
    prefix="/documents/types",
    tags=["HR Document Types"]
)

document_requests_router = APIRouter(
    prefix="/document-requests",
    tags=["HR Document Requests"]
)


# --------------------------------------------------
# 1. GET DOCUMENT TYPES
# GET /documents/types
# --------------------------------------------------

@document_types_router.get(
    "",
    response_model=list[HRDocumentTypesOut]
)
def list_document_types(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return get_active_document_types(
        db,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 2. CREATE DOCUMENT REQUEST
# POST /document-requests
# --------------------------------------------------

@document_requests_router.post(
    "",
    response_model=HRDocumentRequestOut,
    status_code=status.HTTP_201_CREATED
)
def create_document_request(
    request_data: HRDocumentRequestCreate,
    current_user=Depends(
        require_permission("document.request")
    ),
    db: Session = Depends(get_db)
):

    # Identify the employee from the authenticated user.
    employee_id = current_user.employee_id

    employee = get_employee_by_id(
        db,
        employee_id
    )

    if employee is None or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee profile is inactive or unavailable"
        )

    # Find the requested document type.
    document_type = get_document_type_by_code(
        db,
        request_data.document_type_code
    )

    if document_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )

    if not document_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document type is inactive"
        )

    # Determine initial status.
    if document_type.requires_hr_approval:
        initial_status = "Pending"
        history_comments = "Document request submitted; HR approval required."
    else:
        initial_status = "Processing"
        history_comments = (
            "Document request submitted; HR approval is not required. "
            "Awaiting document fulfilment."
        )

    request_record = {
        "employee_id": employee_id,
        "document_type_code": request_data.document_type_code,
        "purpose": request_data.purpose,
        "status": initial_status
    }

    try:
        return create_document_request_with_history(
            db,
            request_record,
            current_user.user_id,
            history_comments
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document request conflicts with existing records"
        )


# --------------------------------------------------
# 3. GET OWN DOCUMENT REQUESTS
# GET /document-requests/me
# --------------------------------------------------

@document_requests_router.get(
    "/me",
    response_model=list[HRDocumentRequestOut]
)
def get_my_document_requests(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    return get_employee_document_requests(
        db,
        current_user.employee_id,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 4. GET DOCUMENT REQUEST BY ID
# GET /document-requests/{request_id}
# --------------------------------------------------

@document_requests_router.get(
    "/{request_id}",
    response_model=HRDocumentRequestOut
)
def get_document_request_details(
    request_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    request = get_document_request_by_id(
        db,
        request_id
    )

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document request not found"
        )

    # Owner can view their own request.
    if current_user.employee_id == request.employee_id:
        return request

    # Check whether the user is an authorised HR processor.
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    if "document.process" in permission_codes:
        return request

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this document request"
    )


# --------------------------------------------------
# 5. PROCESS DOCUMENT REQUEST
# PATCH /document-requests/{request_id}
# --------------------------------------------------

@document_requests_router.patch(
    "/{request_id}",
    response_model=HRDocumentRequestOut
)
def process_document_request(
    request_id: int,
    update_data: HRDocumentRequestUpdate,
    current_user=Depends(
        require_permission("document.process")
    ),
    db: Session = Depends(get_db)
):

    request = get_document_request_by_id(
        db,
        request_id
    )

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document request not found"
        )

    if current_user.employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Processing user is not linked to an employee"
        )

    processor = get_employee_by_id(
        db,
        current_user.employee_id
    )

    if processor is None or not processor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR processor employee profile is inactive or unavailable"
        )

    # Allowed status transitions.
    allowed_transitions = {
        "Pending": {"Processing", "Rejected"},
        "Processing": {"Processing", "Completed", "Rejected"},
        "Completed": set(),
        "Rejected": set()
    }

    new_status = update_data.status

    allowed_statuses = allowed_transitions.get(
        request.status,
        set()
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot change document request status "
                f"from {request.status} to {new_status}"
            )
        )

    update_values = update_data.model_dump(
        exclude_unset=True
    )

    try:
        return update_document_request_with_history(
            db,
            request,
            update_values,
            current_user.user_id,
            current_user.employee_id
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document request processing conflicts with existing records"
        )