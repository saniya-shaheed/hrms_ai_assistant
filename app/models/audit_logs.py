from datetime import date
from sqlalchemy import JSON, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class AuditLogs(Base):
    __tablename__ = "audit_logs"

    audit_log_id = Column(Integer, nullable=False, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    action = Column(String(200), nullable=False, unique=True)
    entity_type = Column(String(100))
    entity_id = Column(String(200), default=True)
    details = Column(JSON, default=date.today, nullable=False)
    created_at = Column(Date, default=date.today, onupdate=date.today, index=True)

    actor_user = relationship("Users", back_populates="audit_logs")