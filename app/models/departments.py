from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class Departments(Base):
    __tablename__ = "departments"

    department_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    department_name = Column(String(100), nullable=False, unique=True, index=True)
    department_code = Column(String(50), unique=True, index=True)
    parent_department_id = Column(BigInteger, ForeignKey("departments.department_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    parent_department = relationship("Departments", remote_side=[department_id], back_populates="sub_department")
    sub_department = relationship("Departments", back_populates="parent_department")
    employees = relationship("Employees", back_populates="department")
    hr_policies = relationship("HRPolicies", back_populates="department")