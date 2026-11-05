from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from pgvector.sqlalchemy import HALFVEC
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT, TSVECTOR

class HRPolicyChunks(Base):
    __tablename__ = "hr_policy_chunks"

    policy_chunk_id = Column(Integer, primary_key=True, nullable=False, index=True)
    policy_version_id = Column(Integer, ForeignKey("hr_policy_versions.policy_version_id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    section_heading = Column(String(200))
    chunk_text = Column(String(2000), nullable=False)
    page_number = Column(Integer)
    source_reference = Column(String(200))
    embedding_model = Column(String(100), nullable=False, default="gemini-embedding-001")
    embedding_dimension = Column(Integer, nullable=False, default=3072)
    embedding = Column(ARRAY(FLOAT),nullable=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)
    search_vector = Column(TSVECTOR)

    policy_version = relationship("HRPolicyVersions", back_populates="policy_chunks")