from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.authorization import require_role
from app.models.users import Users
from app.schema.auth import LoginRequest, TokenResponse
from app.crud.users import get_user_by_email, get_user_roles
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, login_data.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    access_token = create_access_token(user.user_id)

    return TokenResponse(
        access_token=access_token
    )

@router.get("/me")
def get_me(current_user: Users = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "employee_id": current_user.employee_id,
        "is_active": current_user.is_active
    }

@router.get("/my-roles")
def get_my_roles(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roles = get_user_roles(db, current_user.user_id)

    return {
        "user_id": current_user.user_id,
        "roles": [role.role_name for role in roles]
    }

@router.get("/employee-only")
def employee_only(
    current_user = Depends(require_role("Employee"))
):
    return {
        "message": "Employee access granted",
        "user_id": current_user.user_id
    }

@router.get("/hr-only")
def hr_only(
    current_user = Depends(require_role("HR"))
):
    return {
        "message": "HR access granted",
        "user_id": current_user.user_id
    }