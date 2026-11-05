from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class HRPolicies(Base):
    __tablename__ = "hr_policies"

    policy_id = Column(Integer, nullable=False, primary_key=True, index=True)
    policy_code = Column(String(100), nullable=False, unique=True)
    policy_title = Column(String(200), nullable=False)
    policy_category = Column(String(100), nullable=False)
    description = Column(String(500))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    owner_user_id = Column(Integer, ForeignKey("users.user_id"))
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    department = relationship("Departments", back_populates="hr_policies")
    user = relationship("Users", back_populates="hr_policies")
    policy_versions = relationship("HRPolicyVersions", back_populates="policy")