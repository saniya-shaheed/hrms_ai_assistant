from sqlalchemy import Column, Date, ForeignKey, Integer, String, BigInteger, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Timesheets(Base):
    __tablename__ = "timesheets"

    timesheet_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    submitted_at = Column(Date)
    approved_at = Column(Date)
    total_hours = Column(Integer, nullable=False, default=0)
    employee_comments = Column(Text)
    reviewer_comments = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employees", back_populates="time_sheets")
    timesheet_entries = relationship("TimesheetEntries", back_populates="timesheet")
    timesheet_approvals = relationship("TimesheetApprovals", back_populates="timesheet")

    