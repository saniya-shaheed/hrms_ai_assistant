from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class HRPolicyVersions(Base):
    __tablename__ = "hr_policy_versions"

    policy_version_id = Column(Integer, primary_key=True, nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("hr_policies.policy_id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_label = Column(String(50))
    status = Column(String(50), nullable=False, default="draft")
    effective_from = Column(Date)
    effective_to = Column(Date)
    submitted_at = Column(Date, default=date.today)
    approved_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    approved_at = Column(Date)
    published_at = Column(Date)
    source_file_name = Column(String(200))
    source_reference = Column(String(200))
    change_summary = Column(String(500))
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    policy = relationship("HRPolicies", back_populates="policy_versions")
    approved_by_user = relationship("Users", foreign_keys=[approved_by_user_id])
    created_by_user = relationship("Users", foreign_keys=[created_by_user_id])
    policy_chunks = relationship("HRPolicyChunks", back_populates="policy_version")
