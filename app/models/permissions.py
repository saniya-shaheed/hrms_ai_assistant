from sqlalchemy import BigInteger, Column, DateTime, String, Text, func
from app.database import Base

class Permissions(Base):
    __tablename__ = "permissions"

    permission_id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    permission_code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, unique=True)
    created_at = Column(DateTime, default=func.now())


    