from sqlalchemy import BigInteger, DateTime, func, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveBalances(Base):
    __tablename__ = "leave_balances"

    leave_balance_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False)
    leave_type_code = Column(String(100), ForeignKey("leave_types.leave_type_code"), nullable=False)
    entitlement_days = Column(Integer, nullable=False, default=0)
    used_days = Column(Integer, nullable=False, default=0)
    balance_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employees", back_populates="leave_balances")
    leave_type = relationship("LeaveTypes", back_populates="leave_balances")
    leave_transactions = relationship("LeaveTransactions", back_populates="leave_balance")

    