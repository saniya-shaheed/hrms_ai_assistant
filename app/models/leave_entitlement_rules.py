from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveEntitlementRules(Base):
    __tablename__ = "leave_entitlement_rules"

    entitlement_rule_id = Column(Integer, nullable=False, primary_key=True, index=True)
    leave_type__id = Column(Integer, ForeignKey("leave_types.leave_type_id"), nullable=False, unique=True, index=True)
    employmenet_category = Column(String(100), nullable=False, default="All")
    entitlement_days = Column(Integer, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    leave_type = relationship("LeaveTypes", back_populates="leave_entitlement_rules")

    