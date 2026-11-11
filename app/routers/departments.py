from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.departments import get_all_departments
from app.schema.departments import DepartmentCreate, DepartmentOut, DepartmentUpdate
from app.dependencies.authorization import require_permission


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.get("/", response_model=list[DepartmentOut])
def list_departments(
    current_user=Depends(
        require_permission("department.read")
    ),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    departments = get_all_departments(
        db,
        skip=skip,
        limit=limit
    )

    return departments

from app.crud.departments import (
    get_all_departments,
    get_department_by_id,
    get_department_by_name,
    get_department_by_code,
    create_department_record,
    update_department_record
)

# Helper function to check circular department relationships
def creates_department_cycle(
    db: Session,
    department_id: int,
    proposed_parent_id: int
):
    current_id = proposed_parent_id
    visited = set()

    while current_id is not None:

        # Department cannot become its own parent
        if current_id == department_id:
            return True

        # Prevent infinite traversal if existing data has a cycle
        if current_id in visited:
            return True

        visited.add(current_id)

        parent = get_department_by_id(db, current_id)

        if parent is None:
            return False

        current_id = parent.parent_department_id

    return False


# 1. GET ALL DEPARTMENTS
@router.get(
    "/",
    response_model=list[DepartmentOut]
)
def list_departments(
    current_user=Depends(
        require_permission("department.read")
    ),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    departments = get_all_departments(
        db,
        skip=skip,
        limit=limit
    )

    return departments


# 2. GET DEPARTMENT BY ID
@router.get(
    "/{department_id}",
    response_model=DepartmentOut
)
def get_department(
    department_id: int,
    current_user=Depends(
        require_permission("department.read")
    ),
    db: Session = Depends(get_db)
):
    department = get_department_by_id(
        db,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return department


# 3. CREATE DEPARTMENT
@router.post(
    "/",
    response_model=DepartmentOut,
    status_code=status.HTTP_201_CREATED
)
def create_department(
    department_data: DepartmentCreate,
    current_user=Depends(
        require_permission("department.create")
    ),
    db: Session = Depends(get_db)
):

    # Check duplicate department name
    existing_name = get_department_by_name(
        db,
        department_data.department_name
    )

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department name already exists"
        )

    # Check duplicate department code
    existing_code = get_department_by_code(
        db,
        department_data.department_code
    )

    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department code already exists"
        )

    # Validate parent department
    if department_data.parent_department_id is not None:

        parent = get_department_by_id(
            db,
            department_data.parent_department_id
        )

        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent department not found"
            )

    try:
        department = create_department_record(
            db,
            department_data.model_dump()
        )

        return department

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department conflicts with existing database records"
        )


# 4. UPDATE DEPARTMENT
@router.patch(
    "/{department_id}",
    response_model=DepartmentOut
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    current_user=Depends(
        require_permission("department.update")
    ),
    db: Session = Depends(get_db)
):

    # Find department
    department = get_department_by_id(
        db,
        department_id
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Get only fields supplied in the request
    update_data = department_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Required fields cannot be NULL
    required_fields = [
        "department_name",
        "department_code"
    ]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    # Check duplicate department name
    if update_data.get("department_name") is not None:

        existing_name = get_department_by_name(
            db,
            update_data["department_name"],
            exclude_department_id=department_id
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists"
            )

    # Check duplicate department code
    if update_data.get("department_code") is not None:

        existing_code = get_department_by_code(
            db,
            update_data["department_code"],
            exclude_department_id=department_id
        )

        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department code already exists"
            )

    # Validate parent department when supplied
    if "parent_department_id" in update_data:

        parent_id = update_data["parent_department_id"]

        if parent_id is not None:

            parent = get_department_by_id(
                db,
                parent_id
            )

            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent department not found"
                )

            # Check for circular hierarchy
            if creates_department_cycle(
                db,
                department_id,
                parent_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular department hierarchy is not allowed"
                )

    try:
        updated_department = update_department_record(
            db,
            department,
            update_data
        )

        return updated_department

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department update conflicts with existing database records"
        )