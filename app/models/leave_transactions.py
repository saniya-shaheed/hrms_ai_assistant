from sqlalchemy import Column, DateTime, ForeignKey, BigInteger, Text, Integer, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class LeaveTransactions(Base):
    __tablename__ = "leave_transactions"

    leave_transaction_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False)
    leave_balance_id = Column(BigInteger, ForeignKey("leave_balances.leave_balance_id"), nullable=False)
    leave_request_id = Column(BigInteger, ForeignKey("leave_requests.leave_request_id"))
    transaction_type = Column(String(100), nullable=False)
    days_delta = Column(Integer, nullable=False)
    notes = Column(Text)
    actor_user_id = Column(BigInteger, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=func.now())

    employee = relationship("Employees", back_populates="leave_transactions")
    leave_balance = relationship("LeaveBalances", back_populates="leave_transactions")
    leave_request = relationship("LeaveRequests", back_populates="leave_transactions")
    actor_user = relationship("Users", back_populates="leave_transactions")

    