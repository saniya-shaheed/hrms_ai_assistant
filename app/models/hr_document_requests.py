from sqlalchemy import Column, DateTime, ForeignKey, BigInteger, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class HRDocumentRequests(Base):
    __tablename__ = "hr_document_requests"

    document_request_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False)
    document_type_code = Column(String(100), ForeignKey("hr_document_types.document_type_code"), nullable=False)
    purpose = Column(Text)
    status = Column(String(100), default="Pending")
    requested_at = Column(DateTime, default=func.now())
    processed_by_employee_id = Column(BigInteger, ForeignKey("employees.employee_id"))
    processed_at = Column(DateTime)
    remarks = Column(Text)
    document_reference = Column(String(500))

    employee = relationship("Employees", back_populates="hr_document_requests")
    document_type = relationship("HRDocumentTypes", back_populates="hr_document_requests")
    processed_employee = relationship("Employees", back_populates="hr_document_requests")
    history = relationship("HRDocumentRequestHistory", back_populates="document_request")
    