from sqlalchemy import Column, Date, ForeignKey, Integer, String, BigInteger, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.database import Base

class HRPolicyVersions(Base):
    __tablename__ = "hr_policy_versions"

    policy_version_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    policy_id = Column(BigInteger, ForeignKey("hr_policies.policy_id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_label = Column(String(50))
    status = Column(String(50), nullable=False, default="draft")
    effective_from = Column(Date)
    effective_to = Column(Date)
    submitted_at = Column(DateTime)
    approved_by_user_id = Column(BigInteger, ForeignKey("users.user_id"))
    approved_at = Column(DateTime)
    published_at = Column(DateTime)
    source_file_name = Column(String(200))
    source_reference = Column(Text)
    change_summary = Column(Text)
    created_by_user_id = Column(BigInteger, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    policy = relationship("HRPolicies", back_populates="policy_versions")
    approved_by_user = relationship("Users", foreign_keys=[approved_by_user_id])
    created_by_user = relationship("Users", foreign_keys=[created_by_user_id])
    policy_chunks = relationship("HRPolicyChunks", back_populates="policy_version")
