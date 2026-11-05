from sqlalchemy import Boolean, Column, DateTime, BigInteger, Text, Integer, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveTypes(Base):
    __tablename__ = "leave_types"

    leave_type_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    leave_type_code = Column(String(50), nullable=False, unique=True, index=True)
    leave_type_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_paid = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)
    min_notice_calender_days = Column(Integer, default=0)
    max_consecutive_days = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    leave_entitlement_rules = relationship("LeaveEntitlementRules", back_populates="leave_type")
    leave_balances = relationship("LeaveBalances", back_populates="leave_type")
    leave_requests = relationship("LeaveRequests", back_populates="leave_type")