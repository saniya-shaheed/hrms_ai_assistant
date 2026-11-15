from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Date,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
    func
)

from sqlalchemy.orm import relationship
from app.database import Base


class Timesheets(Base):
    __tablename__ = "timesheets"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "period_start",
            name="uq_timesheet_employee_period"
        ),
    )

    timesheet_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        index=True
    )

    employee_id = Column(
        BigInteger,
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="draft",
        server_default="draft"
    )

    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    total_hours = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    employee_comments = Column(Text)
    reviewer_comments = Column(Text)

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

    employee = relationship(
        "Employees",
        back_populates="time_sheets"
    )

    timesheet_entries = relationship(
        "TimesheetEntries",
        back_populates="timesheet"
    )

    timesheet_approvals = relationship(
        "TimesheetApprovals",
        back_populates="timesheet"
    )