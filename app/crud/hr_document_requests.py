from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.hr_document_requests import HRDocumentRequests
from app.models.hr_document_request_history import HRDocumentRequestHistory


def get_document_request_by_id(
    db: Session,
    request_id: int
):
    return (
        db.query(HRDocumentRequests)
        .filter(
            HRDocumentRequests.document_request_id == request_id
        )
        .first()
    )


def get_employee_document_requests(
    db: Session,
    employee_id: int,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(HRDocumentRequests)
        .filter(
            HRDocumentRequests.employee_id == employee_id
        )
        .order_by(HRDocumentRequests.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_document_request_with_history(
    db: Session,
    request_data: dict,
    actor_user_id: int,
    history_comments: str
):
    request = HRDocumentRequests(**request_data)

    try:
        db.add(request)

        # Generate the request ID before creating its history.
        db.flush()

        history = HRDocumentRequestHistory(
            document_request_id=request.document_request_id,
            previous_status=None,
            new_status=request.status,
            action_by_user_id=actor_user_id,
            comments=history_comments
        )

        db.add(history)

        # Save the request and history together.
        db.commit()

        db.refresh(request)

        return request

    except Exception:
        db.rollback()
        raise


def update_document_request_with_history(
    db: Session,
    request: HRDocumentRequests,
    update_data: dict,
    actor_user_id: int,
    actor_employee_id: int
):
    previous_status = request.status
    new_status = update_data["status"]

    try:
        request.status = new_status

        if "remarks" in update_data:
            request.remarks = update_data["remarks"]

        if "document_reference" in update_data:
            request.document_reference = update_data["document_reference"]

        request.processed_by_employee_id = actor_employee_id
        request.processed_at = func.now()

        history = HRDocumentRequestHistory(
            document_request_id=request.document_request_id,
            previous_status=previous_status,
            new_status=new_status,
            action_by_user_id=actor_user_id,
            comments=update_data.get("remarks")
        )

        db.add(history)

        # Save request changes and history together.
        db.commit()

        db.refresh(request)

        return request

    except Exception:
        db.rollback()
        raise