from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveRequests(Base):
    __tablename__ = "leave_requests"

    leave_request_id = Column(Integer, nullable=False, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_code = Column(String(100), ForeignKey("leave_types.leave_type_code"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(String(500))
    status = Column(String(100), nullable=False, default="Pending")
    submitted_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    employee = relationship("Employees", back_populates="leave_requests")
    leave_type = relationship("LeaveTypes", back_populates="leave_requests")
    leave_approvals = relationship("LeaveApprovals", back_populates="leave_request")
    leave_transactions = relationship("LeaveTransactions", back_populates="leave_request")

    