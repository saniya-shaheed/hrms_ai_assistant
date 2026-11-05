from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), unique=True, index=True)
    password_hash = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    employee = relationship("Employees", back_populates="user")
    user_roles = relationship("UserRoles", back_populates="user")
    audit_logs = relationship("AuditLogs", back_populates="actor_user")
    leave_transactions = relationship("LeaveTransactions", back_populates="actor_user")
    hr_document_requests = relationship("HRDocumentRequestHistory", back_populates="action_user")
    ai_conversations = relationship("AIConversations", back_populates="user")
    ai_tool_executions = relationship("AIToolExecutions", back_populates="user")
    hr_policies = relationship("HRPolicies", back_populates="user")
    hr_policy_versions = relationship("HRPolicyVersions", back_populates="created_by_user")