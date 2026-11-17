from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text
from app.database import Base, engine
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app import models
from app.routers import auth, employees, departments, users, leave_types, leave_entitlement_rules, leave_balances, leave_requests, public_holidays
from app.routers.roles import roles_router, permissions_router, user_roles_router
from app.routers.leave_approvals import pending_router, decision_router
from app.routers.hr_documents import document_types_router, document_requests_router
from app.routers import timesheets
from app.routers import conversations
from app.routers import chat

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
# app.include_router(employees.router)
# app.include_router(departments.router)
# app.include_router(roles_router)
# app.include_router(permissions_router)
# app.include_router(user_roles_router)
# app.include_router(users.router)
# app.include_router(leave_types.router)
# app.include_router(leave_entitlement_rules.router)
# app.include_router(leave_balances.router)
# app.include_router(leave_requests.router)
# app.include_router(pending_router)
# app.include_router(decision_router)
# app.include_router(public_holidays.router)
# app.include_router(document_types_router)
# app.include_router(document_requests_router)
# app.include_router(timesheets.router)
app.include_router(conversations.router)
app.include_router(chat.router)






