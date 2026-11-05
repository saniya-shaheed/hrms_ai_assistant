from sqlalchemy import Column, DateTime, ForeignKey, BigInteger, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class HRDocumentRequestHistory(Base):
    __tablename__ = "hr_document_request_history"

    history_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    document_request_id = Column(BigInteger, ForeignKey("hr_document_requests.document_request_id"), nullable=False)
    previous_status = Column(String(100))
    new_status = Column(String(100), nullable=False)
    action_by_user_id = Column(BigInteger, ForeignKey("users.user_id"))
    comments = Column(Text)
    action_at = Column(DateTime, default=func.now(), nullable=False)

    document_request = relationship("HRDocumentRequests", back_populates="history")
    action_user = relationship("Users", back_populates="hr_document_requests")

    