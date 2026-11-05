from datetime import date
from sqlalchemy import JSON, Column, Date, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.database import Base

class AIConversations(Base):
    __tablename__ = "ai_conversations"

    conversation_id = Column(Integer, primary_key=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200))
    status = Column(String(50), default="active")
    started_at = Column(Date, default=date.today)
    last_message_at = Column(Date, default=date.today, onupdate=date.today)
    ended_at = Column(Date)
    meta_data = Column(JSON, default=lambda:{})

    user = relationship("Users", back_populates="ai_conversations")
    messages = relationship("AIMessages", back_populates="conversation")
    tool_executions = relationship("AIToolExecutions", back_populates="conversation")
    

    