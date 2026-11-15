from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Text,
    ForeignKey,
    func
)

from sqlalchemy.orm import relationship
from app.database import Base


class TimesheetApprovals(Base):
    __tablename__ = "timesheet_approvals"

    timesheet_approval_id = Column(
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

    approver_employee_id = Column(
        BigInteger,
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    decision = Column(String(100), nullable=False)
    comments = Column(Text)

    decided_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now()
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now()
    )

    timesheet = relationship(
        "Timesheets",
        back_populates="timesheet_approvals"
    )

    approver_employee = relationship(
        "Employees",
        back_populates="timesheet_approvals"
    )