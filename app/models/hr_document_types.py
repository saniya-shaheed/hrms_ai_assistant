from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class HRDocumentTypes(Base):
    __tablename__ = "hr_document_types"

    document_type_id = Column(Integer, nullable=False, primary_key=True, index=True)
    document_type_code = Column(String(100), nullable=False, unique=True)
    document_type_name = Column(String(200), nullable=False)
    description = Column(String(500))
    requires_hr_approval = Column(Boolean, nullable=False, default= True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    hr_document_requests = relationship("HRDocumentRequests", back_populates="document_type")

    