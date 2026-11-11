from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db

from app.core.security import hash_password

from app.dependencies.authorization import (
    require_permission,
    require_role
)

from app.crud.users import (
    get_user_by_id,
    get_user_by_employee_id,
    get_all_users,
    create_user_record,
    update_user_record,
    update_user_password
)

from app.crud.employees import get_employee_by_id

from app.schema.users import (
    UserCreate,
    UserUpdate,
    UserStatusUpdate,
    UserPasswordReset,
    UserOut
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# --------------------------------------------------
# 1. CREATE USER
# POST /users
# --------------------------------------------------

@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    current_user=Depends(
        require_permission("user.create")
    ),
    db: Session = Depends(get_db)
):

    # Check whether employee exists
    employee = get_employee_by_id(
        db,
        user_data.employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # An active account cannot belong to an inactive employee
    if employee.is_active is False and user_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an active account for an inactive employee"
        )

    # Check whether employee already has a login account
    existing_user = get_user_by_employee_id(
        db,
        user_data.employee_id
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already has a user account"
        )

    # Hash the password before storing it
    password_hash = hash_password(user_data.password)

    user_record = {
        "employee_id": user_data.employee_id,
        "password_hash": password_hash,
        "is_active": user_data.is_active
    }

    try:
        return create_user_record(db, user_record)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User account conflicts with existing records"
        )


# --------------------------------------------------
# 2. GET ALL USERS
# GET /users
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[UserOut]
)
def list_users(
    current_user=Depends(
        require_permission("user.read")
    ),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):

    return get_all_users(
        db,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 3. GET USER BY ID
# GET /users/{user_id}
# --------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserOut
)
def get_user(
    user_id: int,
    current_user=Depends(
        require_permission("user.read")
    ),
    db: Session = Depends(get_db)
):

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# 4. UPDATE USER
# PATCH /users/{user_id}
# --------------------------------------------------

@router.patch(
    "/{user_id}",
    response_model=UserOut
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user=Depends(
        require_permission("user.update")
    ),
    db: Session = Depends(get_db)
):

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    if "employee_id" in update_data:

        new_employee_id = update_data["employee_id"]

        if new_employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Employee ID cannot be null"
            )

        employee = get_employee_by_id(
            db,
            new_employee_id
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Prevent two user accounts linking to the same employee
        existing_user = get_user_by_employee_id(
            db,
            new_employee_id
        )

        if (
            existing_user is not None
            and existing_user.user_id != user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee already has a user account"
            )

        if employee.is_active is False and user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot link an active account to an inactive employee"
            )

    try:
        return update_user_record(
            db,
            user,
            update_data
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User update conflicts with existing records"
        )


# --------------------------------------------------
# 5. UPDATE USER STATUS
# PATCH /users/{user_id}/status
# --------------------------------------------------

@router.patch(
    "/{user_id}/status",
    response_model=UserOut
)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_user=Depends(
        require_role("Administrator")
    ),
    db: Session = Depends(get_db)
):

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent administrator from accidentally deactivating their own account
    if (
        current_user.user_id == user_id
        and status_data.is_active is False
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    # Prevent activation of an account linked to an inactive employee
    if status_data.is_active:
        employee = get_employee_by_id(
            db,
            user.employee_id
        )

        if employee is None or not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot activate an account linked to an inactive employee"
            )

    try:
        return update_user_record(
            db,
            user,
            {"is_active": status_data.is_active}
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update user status"
        )


# --------------------------------------------------
# 6. RESET USER PASSWORD
# POST /users/{user_id}/reset-password
# --------------------------------------------------

@router.post(
    "/{user_id}/reset-password"
)
def reset_user_password(
    user_id: int,
    reset_data: UserPasswordReset,
    current_user=Depends(
        require_role("Administrator")
    ),
    db: Session = Depends(get_db)
):

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash the new password
    password_hash = hash_password(
        reset_data.new_password
    )

    try:
        update_user_password(
            db,
            user,
            password_hash
        )

        return {
            "message": "User password reset successfully",
            "user_id": user.user_id
        }

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset user password"
        )