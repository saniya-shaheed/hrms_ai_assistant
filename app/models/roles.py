from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Roles(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False, index=True)
    description = Column(String(300))
    created_at = Column(Date, default=date.today)

    user_roles = relationship("UserRoles", back_populates="role")

    