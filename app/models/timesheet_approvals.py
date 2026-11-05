from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class TimesheetApprovals(Base):
    __tablename__ = "timesheet_approvals"

    timesheet_approval_id = Column(Integer, nullable=False, primary_key=True, index=True)
    timesheet_id = Column(Integer, ForeignKey("timesheets.timesheet_id"), nullable=False)
    approver_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    decision = Column(String(100), nullable=False) 
    comments = Column(String(500))
    decided_at = Column(Date, default=date.today)
    created_at = Column(Date, default=date.today)

    timesheet = relationship("Timesheets", back_populates="timesheet_approvals")
    approver_employee = relationship("Employees", back_populates="timesheet_approvals")