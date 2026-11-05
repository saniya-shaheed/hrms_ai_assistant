from datetime import date

from sqlalchemy import Column, Date, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer,ForeignKey("users.user_id"),primary_key=True,nullable=False)
    role_id = Column(Integer,ForeignKey("roles.role_id"),primary_key=True,nullable=False)
    assigned_at = Column(Date, default=date.today)

    user = relationship("Users", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")