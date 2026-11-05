from sqlalchemy import JSON, Column, DateTime, ForeignKey, BigInteger, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class AIToolExecutions(Base):
    __tablename__ = "ai_tool_executions"

    tool_execution_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    conversation_id = Column(BigInteger, ForeignKey("ai_conversations.conversation_id"), nullable=False)
    message_id = Column(BigInteger, ForeignKey("ai_messages.message_id"))
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    tool_name = Column(String(100), nullable=False)
    input_arguments = Column(JSON, default=lambda:{})
    execution_status = Column(String(100), default="started")
    result_summary = Column(Text)
    error_code = Column(String(100))
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)

    conversation = relationship("AIConversations", back_populates="tool_executions")
    message = relationship("AIMessages", back_populates="tool_executions")
    user = relationship("Users", back_populates="ai_tool_executions")

