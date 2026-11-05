from sqlalchemy import JSON, Column, DateTime, ForeignKey, BigInteger, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class AIConversations(Base):
    __tablename__ = "ai_conversations"

    conversation_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200))
    status = Column(String(50), default="active")
    started_at = Column(DateTime, default=func.now())
    last_message_at = Column(DateTime)
    ended_at = Column(DateTime)
    meta_data = Column(JSON, default=lambda:{})

    user = relationship("Users", back_populates="ai_conversations")
    messages = relationship("AIMessages", back_populates="conversation")
    tool_executions = relationship("AIToolExecutions", back_populates="conversation")
    

    