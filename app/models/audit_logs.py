from sqlalchemy import JSON, Column, DateTime, ForeignKey, BigInteger, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLogs(Base):
    __tablename__ = "audit_logs"

    audit_log_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    actor_user_id = Column(BigInteger, ForeignKey("users.user_id"), index=True)
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(String(200))
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

    actor_user = relationship("Users", back_populates="audit_logs")