from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Text, SmallInteger, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, TSVECTOR

class HRPolicyChunks(Base):
    __tablename__ = "hr_policy_chunks"

    policy_chunk_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    policy_version_id = Column(BigInteger, ForeignKey("hr_policy_versions.policy_version_id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    section_heading = Column(String(200))
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer)
    source_reference = Column(Text)
    embedding_model = Column(String(100), nullable=False, default="gemini-embedding-001")
    embedding_dimension = Column(SmallInteger, nullable=False, default=3072)
    embedding = Column(ARRAY(FLOAT),nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    search_vector = Column(TSVECTOR)

    policy_version = relationship("HRPolicyVersions", back_populates="policy_chunks")