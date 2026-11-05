from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Timesheets(Base):
    __tablename__ = "timesheets"

    timesheet_id = Column(Integer, primary_key=True, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    submitted_at = Column(Date)
    approved_at = Column(Date)
    total_hours = Column(Integer, nullable=False, default=0)
    employee_comments = Column(String(500))
    reviewer_comments = Column(String(500))
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    employee = relationship("Employees", back_populates="time_sheets")
    timesheet_entries = relationship("TimesheetEntries", back_populates="timesheet")
    timesheet_approvals = relationship("TimesheetApprovals", back_populates="timesheet")

    