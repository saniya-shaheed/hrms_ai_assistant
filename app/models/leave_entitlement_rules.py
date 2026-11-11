from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship

from app.database import Base


class LeaveEntitlementRules(Base):
    __tablename__ = "leave_entitlement_rules"

    entitlement_rule_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        index=True
    )

    leave_type_id = Column(
        BigInteger,
        ForeignKey("leave_types.leave_type_id"),
        nullable=False,
        index=True
    )

    employment_category = Column(
        String(100),
        nullable=False,
        default="All",
        server_default="All"
    )

    entitlement_days = Column(Integer, nullable=False)

    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

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

    leave_type = relationship(
        "LeaveTypes",
        back_populates="leave_entitlement_rules"
    )