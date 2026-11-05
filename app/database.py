from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()

DATABASE_URL = os.getenv("HRMS_DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base() 
def get_db(): 
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
