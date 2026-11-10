from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.users import get_user_permissions
from app.database import get_db
from app.crud.employees import create_employee_record, get_all_employees, get_employee_by_code, get_employee_by_email, get_employee_by_id, update_employee_record
from app.dependencies.auth import get_current_user
from app.models.departments import Departments
from app.schema.employees import EmployeesCreate, EmployeesOut, EmployeesUpdate
from app.dependencies.authorization import require_permission


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.get("/me", response_model=EmployeesOut)
def get_my_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_by_id(
        db,
        current_user.employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )

    return employee

@router.get("/", response_model=list[EmployeesOut])
def list_employees(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR and Administrator: View all employees
    if "employee.read_all" in permission_codes:
        return get_all_employees(
            db,
            skip=skip,
            limit=limit
        )

    # Manager: View assigned direct reports
    if "employee.read_team" in permission_codes:

        if current_user.employee_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not linked to an employee profile"
            )

        return get_all_employees(
            db,
            skip=skip,
            limit=limit,
            manager_employee_id=current_user.employee_id
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view the employee directory"
    )

@router.get("/{employee_id}", response_model=EmployeesOut)
def get_employee_details(
    employee_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Allow employees to view their own profile
    if current_user.employee_id == employee.employee_id:
        return employee

    # Retrieve current user's permissions
    permissions = get_user_permissions(
        db,
        current_user.user_id
    )

    permission_codes = {
        permission.permission_code
        for permission in permissions
    }

    # HR and Administrator can view all employee profiles
    if "employee.read_all" in permission_codes:
        return employee

    # Managers can view their assigned employees
    if (
        "employee.read_team" in permission_codes
        and employee.manager_employee_id == current_user.employee_id
    ):
        return employee

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this employee"
    )

@router.post(
    "/",
    response_model=EmployeesOut,
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    employee_data: EmployeesCreate,
    current_user=Depends(
        require_permission("employee.create")
    ),
    db: Session = Depends(get_db)
):
    # Check duplicate employee code
    existing_code = get_employee_by_code(
        db,
        employee_data.employee_code
    )

    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee code already exists"
        )

    # Check duplicate email
    existing_email = get_employee_by_email(
        db,
        employee_data.email
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee email already exists"
        )

    # Validate department
    if employee_data.department_id is not None:
        department = (
            db.query(Departments)
            .filter(
                Departments.department_id ==
                employee_data.department_id
            )
            .first()
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # Validate reporting manager
    if employee_data.manager_employee_id is not None:
        manager = get_employee_by_id(
            db,
            employee_data.manager_employee_id
        )

        if manager is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reporting manager not found"
            )

    try:
        employee = create_employee_record(
            db,
            employee_data.model_dump()
        )

        return employee

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee record conflicts with existing data"
        )

@router.patch(
    "/{employee_id}",
    response_model=EmployeesOut
)
def update_employee(
    employee_id: int,
    employee_data: EmployeesUpdate,
    current_user=Depends(
        require_permission("employee.update")
    ),
    db: Session = Depends(get_db)
):
    # Find employee
    employee = get_employee_by_id(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Get only fields supplied in the request
    update_data = employee_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Required database fields cannot be set to NULL
    required_fields = [
        "employee_code",
        "employee_name",
        "email"
    ]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    # Check employee code uniqueness
    if update_data.get("employee_code") is not None:
        existing_code = get_employee_by_code(
            db,
            update_data["employee_code"]
        )

        if (
            existing_code is not None
            and existing_code.employee_id != employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee code already exists"
            )

    # Check email uniqueness
    if update_data.get("email") is not None:
        existing_email = get_employee_by_email(
            db,
            update_data["email"]
        )

        if (
            existing_email is not None
            and existing_email.employee_id != employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee email already exists"
            )

    # Validate department
    if update_data.get("department_id") is not None:
        department = (
            db.query(Departments)
            .filter(
                Departments.department_id ==
                update_data["department_id"]
            )
            .first()
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    # Validate reporting manager
    if "manager_employee_id" in update_data:
        manager_id = update_data["manager_employee_id"]

        if manager_id == employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee cannot be their own manager"
            )

        if manager_id is not None:
            manager = get_employee_by_id(db, manager_id)

            if manager is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reporting manager not found"
                )

    try:
        updated_employee = update_employee_record(
            db,
            employee,
            update_data
        )

        return updated_employee

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee update conflicts with existing data"
        )
