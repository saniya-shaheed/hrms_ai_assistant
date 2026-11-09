from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text
from app.database import Base, engine
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app import models
from app.routers import auth

Base.metadata.create_all(bind=engine)
app = FastAPI() 

@app.get("/")
def home():

    return {
        "message": "AI HRMS API is running"
    }


@app.get("/db-check")
def database_check(db: Session = Depends(get_db)):

    try:

        result = db.execute(text("SELECT 1"))

        return {
            "status": "success",
            "message": "FastAPI connected to PostgreSQL successfully!",
            "database_test": result.scalar()
        }

    except Exception as e:

        return {
            "status": "failed",
            "message": str(e)
        }


app.include_router(auth.router)
