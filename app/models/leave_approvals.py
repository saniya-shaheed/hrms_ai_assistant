from sqlalchemy import Column, ForeignKey, BigInteger, String, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveApprovals(Base):
    __tablename__ = "leave_approvals"

    leave_approval_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    leave_request_id = Column(BigInteger, ForeignKey("leave_requests.leave_request_id"), nullable=False)
    approver_employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False)
    decision = Column(String(200), nullable=False)
    comments = Column(Text)
    decided_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    leave_request = relationship("LeaveRequests", back_populates="leave_approvals")
    approver = relationship("Employees", back_populates="leave_approvals")

    