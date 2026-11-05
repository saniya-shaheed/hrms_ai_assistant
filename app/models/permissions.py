from datetime import date
from sqlalchemy import Column, Date, Integer, String
from app.database import Base

class Permissions(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, nullable=False, index=True)
    permission_code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(300), unique=True)
    created_at = Column(Date, default=date.today)


    