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

from app.dependencies.authorization import require_role

from app.crud.roles import (
    get_all_roles,
    get_role_by_id,
    get_role_by_name,
    create_role_record,
    update_role_record
)

from app.crud.permissions import (
    get_all_permissions,
    get_permission_by_id
)

from app.crud.users import get_user_by_id

from app.crud.user_roles import (
    get_user_role_assignment,
    create_user_role_assignment
)

from app.crud.role_permissions import (
    get_role_permission_assignment,
    create_role_permission_assignment
)

from app.schema.roles import (
    RolesCreate,
    RolesUpdate,
    RolesOut
)

from app.schema.permissions import PermissionsOut

from app.schema.user_roles import (
    UserRolesBase,
    UserRolesOut
)

from app.schema.role_permissions import (
    RolePermissionsBase,
    RolePermissionsOut
)


roles_router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

permissions_router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)

user_roles_router = APIRouter(
    prefix="/users",
    tags=["User Roles"]
)


# --------------------------------------------------
# 1. GET ALL ROLES
# GET /roles
# --------------------------------------------------

@roles_router.get("/", response_model=list[RolesOut])
def list_roles(
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return get_all_roles(db, skip=skip, limit=limit)


# --------------------------------------------------
# 2. CREATE ROLE
# POST /roles
# --------------------------------------------------

@roles_router.post(
    "/",
    response_model=RolesOut,
    status_code=status.HTTP_201_CREATED
)
def create_role(
    role_data: RolesCreate,
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db)
):
    existing_role = get_role_by_name(
        db,
        role_data.role_name
    )

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role name already exists"
        )

    try:
        return create_role_record(
            db,
            role_data.model_dump()
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role conflicts with existing records"
        )


# --------------------------------------------------
# 3. UPDATE ROLE
# PATCH /roles/{role_id}
# --------------------------------------------------

@roles_router.patch(
    "/{role_id}",
    response_model=RolesOut
)
def update_role(
    role_id: int,
    role_data: RolesUpdate,
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db)
):
    role = get_role_by_id(db, role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    update_data = role_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    if "role_name" in update_data:
        if update_data["role_name"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Role name cannot be null"
            )

        existing_role = get_role_by_name(
            db,
            update_data["role_name"],
            exclude_role_id=role_id
        )

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role name already exists"
            )

    try:
        return update_role_record(
            db,
            role,
            update_data
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role update conflicts with existing records"
        )


# --------------------------------------------------
# 4. ASSIGN ROLE TO USER
# POST /users/{user_id}/roles
# --------------------------------------------------

@user_roles_router.post(
    "/{user_id}/roles",
    response_model=UserRolesOut,
    status_code=status.HTTP_201_CREATED
)
def assign_role_to_user(
    user_id: int,
    role_data: UserRolesBase,
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    role = get_role_by_id(db, role_data.role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    existing_assignment = get_user_role_assignment(
        db,
        user_id,
        role_data.role_id
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This role is already assigned to the user"
        )

    try:
        return create_user_role_assignment(
            db,
            user_id,
            role_data.role_id
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role assignment conflicts with existing records"
        )


# --------------------------------------------------
# 5. GET ALL PERMISSIONS
# GET /permissions
# --------------------------------------------------

@permissions_router.get(
    "/",
    response_model=list[PermissionsOut]
)
def list_permissions(
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return get_all_permissions(
        db,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 6. ASSIGN PERMISSION TO ROLE
# POST /roles/{role_id}/permissions
# --------------------------------------------------

@roles_router.post(
    "/{role_id}/permissions",
    response_model=RolePermissionsOut,
    status_code=status.HTTP_201_CREATED
)
def assign_permission_to_role(
    role_id: int,
    permission_data: RolePermissionsBase,
    current_user=Depends(require_role("Administrator")),
    db: Session = Depends(get_db)
):
    role = get_role_by_id(db, role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    permission = get_permission_by_id(
        db,
        permission_data.permission_id
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    existing_assignment = get_role_permission_assignment(
        db,
        role_id,
        permission_data.permission_id
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This permission is already assigned to the role"
        )

    try:
        return create_role_permission_assignment(
            db,
            role_id,
            permission_data.permission_id
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission assignment conflicts with existing records"
        )