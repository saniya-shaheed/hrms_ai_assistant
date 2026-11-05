from sqlalchemy import BigInteger, Column, DateTime, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Roles(Base):
    __tablename__ = "roles"

    role_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

    user_roles = relationship("UserRoles", back_populates="role")

    