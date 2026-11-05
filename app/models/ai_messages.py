from datetime import date
from sqlalchemy import JSON, Column, Date, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from app.database import Base

class AIMessages(Base):
    __tablename__ = "ai_messages"

    message_id = Column(Integer, primary_key=True, nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.conversation_id"), nullable=False)
    sender_type = Column(String(200), nullable=False)
    content = Column(String(500), nullable=False)
    model_name = Column(String(100))
    token_count = Column(Integer)
    meta_data = Column(JSON, default=lambda:{})
    created_at = Column(Date, default=date.today)

    conversation = relationship("AIConversations", back_populates="messages")
    tool_executions = relationship("AIToolExecutions", back_populates="message")
    