from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class RolePermissions(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer,ForeignKey("roles.role_id"),primary_key=True,nullable=False)
    permission_id = Column(Integer,ForeignKey("permissions.permission_id"),primary_key=True,nullable=False)

    role = relationship("Roles", back_populates="role_permissions")
    permission = relationship("Permissions", back_populates="role_permissions")