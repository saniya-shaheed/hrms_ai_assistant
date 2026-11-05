from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class HRDocumentRequests(Base):
    __tablename__ = "hr_document_requests"

    document_request_id = Column(Integer, nullable=False, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    document_type_code = Column(String(100), ForeignKey("hr_document_types.document_type_code"), nullable=False)
    purpose = Column(String(500))
    status = Column(String(100), default="Pending")
    requested_at = Column(Date, default=date.today)
    processed_by_employee_id = Column(Integer, ForeignKey("employees.employee_id"))
    processed_at = Column(Date, default="Pending")
    remarks = Column(String(500), default=date.today)
    document_reference = Column(String(500), default=date.today, onupdate=date.today)

    employee = relationship("Employees", back_populates="hr_document_requests")
    document_type = relationship("HRDocumentTypes", back_populates="hr_document_requests")
    processed_employee = relationship("Employees", back_populates="hr_document_requests")
    history = relationship("HRDocumentRequestHistory", back_populates="document_request")
    