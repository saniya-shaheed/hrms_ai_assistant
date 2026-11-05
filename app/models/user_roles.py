from sqlalchemy import BigInteger, Column, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id = Column(BigInteger,ForeignKey("users.user_id"),primary_key=True,nullable=False)
    role_id = Column(BigInteger,ForeignKey("roles.role_id"),primary_key=True,nullable=False)
    assigned_at = Column(DateTime, default=func.now())

    user = relationship("Users", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")