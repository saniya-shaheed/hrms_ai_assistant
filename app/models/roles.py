from sqlalchemy import BigInteger, Column, DateTime, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base

class Roles(Base):
    __tablename__ = "roles"

    role_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    created_at = Column(
    DateTime,
    nullable=False,
    default=func.now(),
    server_default=func.now()
)

    user_roles = relationship("UserRoles", back_populates="role")
    role_permissions = relationship("RolePermissions", back_populates="role")

    