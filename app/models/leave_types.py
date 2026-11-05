from datetime import date
from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveTypes(Base):
    __tablename__ = "leave_types"

    leave_type_id = Column(Integer, nullable=False, primary_key=True, index=True)
    leave_type_code = Column(String(50), nullable=False, unique=True, index=True)
    leave_type_name = Column(String(100), nullable=False)
    description = Column(String(100))
    is_paid = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    min_notice_calender_days = Column(Integer, default=0)
    max_consecutive_days = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    leave_entitlement_rules = relationship("LeaveEntitlementRules", back_populates="leave_type")
    leave_balances = relationship("LeaveBalances", back_populates="leave_type")
    leave_requests = relationship("LeaveRequests", back_populates="leave_type")