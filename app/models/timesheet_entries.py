from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Date,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    func
)

from sqlalchemy.orm import relationship
from app.database import Base


class TimesheetEntries(Base):
    __tablename__ = "timesheet_entries"

    timesheet_entry_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        index=True
    )

    timesheet_id = Column(
        BigInteger,
        ForeignKey("timesheets.timesheet_id"),
        nullable=False
    )

    work_date = Column(Date, nullable=False)

    hours_worked = Column(Integer, nullable=False)

    task_description = Column(Text)
    project_code = Column(String(100))

    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now()
    )

    timesheet = relationship(
        "Timesheets",
        back_populates="timesheet_entries"
    )