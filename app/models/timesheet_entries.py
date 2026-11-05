from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class TimesheetEntries(Base):
    __tablename__ = "timesheet_entries"

    timesheet_entry_id = Column(Integer, nullable=False, primary_key=True, index=True)
    timesheet_id = Column(Integer, ForeignKey("timesheets.timesheet_id"), nullable=False)
    work_date = Column(Date, nullable=False)
    hours_worked = Column(Integer, nullable=False)
    task_description = Column(String(500))
    project_code = Column(String(100))
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    timesheet = relationship("Timesheets", back_populates="timesheet_entries")


    