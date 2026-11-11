from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    employee_id = Column(BigInteger, ForeignKey("employees.employee_id"), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now())

    employee = relationship("Employees", back_populates="user")
    user_roles = relationship("UserRoles", back_populates="user")
    audit_logs = relationship("AuditLogs", back_populates="actor_user")
    leave_transactions = relationship("LeaveTransactions", back_populates="actor_user")
    hr_document_requests = relationship("HRDocumentRequestHistory", back_populates="action_user")
    ai_conversations = relationship("AIConversations", back_populates="user")
    ai_tool_executions = relationship("AIToolExecutions", back_populates="user")
    hr_policies = relationship("HRPolicies", back_populates="user")
    approved_hr_policy_versions = relationship("HRPolicyVersions", foreign_keys="HRPolicyVersions.approved_by_user_id", back_populates="approved_by_user")
    created_hr_policy_versions = relationship("HRPolicyVersions", foreign_keys="HRPolicyVersions.created_by_user_id", back_populates="created_by_user")