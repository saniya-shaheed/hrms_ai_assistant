from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Departments(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, nullable=False, primary_key=True, index=True)
    department_name = Column(String(100), nullable=False, unique=True, index=True)
    department_code = Column(String(50), unique=True, index=True)
    parent_department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    parent_department = relationship("Departments", remote_side=[department_id], back_populates="sub_department")
    sub_department = relationship("Departments", back_populates="parent_department")
    employees = relationship("Departments", back_populates="department")
    hr_policies = relationship("HRPolicies", back_populates="department")