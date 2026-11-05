from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveApprovals(Base):
    __tablename__ = "leave_approvals"

    leave_approval_id = Column(Integer, nullable=False, primary_key=True, index=True)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.leave_request_id"), nullable=False)
    approver_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    decision = Column(String(200), nullable=False)
    comments = Column(String(500))
    decided_at = Column(Date, default=date.today)
    created_at = Column(Date, default=date.today, onupdate=date.today)

    leave_request = relationship("LeaveRequests", back_populates="leave_approvals")
    approver = relationship("Employees", back_populates="leave_approvals")

    