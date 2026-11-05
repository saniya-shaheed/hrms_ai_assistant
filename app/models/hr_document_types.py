from sqlalchemy import Boolean, Column, ForeignKey, BigInteger, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class HRDocumentTypes(Base):
    __tablename__ = "hr_document_types"

    document_type_id = Column(BigInteger, nullable=False, primary_key=True, index=True)
    document_type_code = Column(String(100), nullable=False, unique=True)
    document_type_name = Column(String(200), nullable=False)
    description = Column(Text)
    requires_hr_approval = Column(Boolean, nullable=False, default= True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    hr_document_requests = relationship("HRDocumentRequests", back_populates="document_type")

    