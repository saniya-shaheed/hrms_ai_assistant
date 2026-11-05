from datetime import date
from sqlalchemy import JSON, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class AIToolExecutions(Base):
    __tablename__ = "ai_tool_executions"

    tool_execution_id = Column(Integer, primary_key=True, nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.conversation_id"), nullable=False)
    message_id = Column(Integer, ForeignKey("ai_messages.message_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    tool_name = Column(String(100), nullable=False)
    input_arguments = Column(JSON, default=lambda:{})
    execution_status = Column(String(100), default="started")
    result_summary = Column(String(500))
    error_code = Column(String(100))
    started_at = Column(Date, default=date.today)
    completed_at = Column(Date)

    conversation = relationship("AIConversations", back_populates="tool_executions")
    message = relationship("AIMessages", back_populates="tool_executions")
    user = relationship("Users", back_populates="ai_tool_executions")

