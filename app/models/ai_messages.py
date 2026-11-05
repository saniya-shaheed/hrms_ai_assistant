from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, BigInteger, func
from sqlalchemy.orm import relationship
from app.database import Base

class AIMessages(Base):
    __tablename__ = "ai_messages"

    message_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    conversation_id = Column(BigInteger, ForeignKey("ai_conversations.conversation_id"), nullable=False)
    sender_type = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    model_name = Column(String(100))
    token_count = Column(Integer)
    meta_data = Column(JSON, default=lambda:{})
    created_at = Column(DateTime, default=func.now())

    conversation = relationship("AIConversations", back_populates="messages")
    tool_executions = relationship("AIToolExecutions", back_populates="message")
    