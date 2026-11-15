from sqlalchemy.orm import Session

from app.models.hr_document_types import HRDocumentTypes


def get_active_document_types(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(HRDocumentTypes)
        .filter(HRDocumentTypes.is_active.is_(True))
        .order_by(HRDocumentTypes.document_type_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_document_type_by_code(
    db: Session,
    document_type_code: str
):
    return (
        db.query(HRDocumentTypes)
        .filter(
            HRDocumentTypes.document_type_code == document_type_code
        )
        .first()
    )