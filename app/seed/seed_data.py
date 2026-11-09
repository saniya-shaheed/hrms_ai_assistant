from app.database import SessionLocal
from app.models import Departments, Roles, Permissions, Employees, Users
from app.core.security import hash_password


def seed_departments(db):
    departments = [
        {
            "department_name": "Information Technology",
            "department_code": "IT",
            "is_active": True,
        },
        {
            "department_name": "Human Resources",
            "department_code": "HR",
            "is_active": True,
        },
        {
            "department_name": "Finance",
            "department_code": "FIN",
            "is_active": True,
        },
    ]

    for data in departments:
        existing = (
            db.query(Departments)
            .filter(
                Departments.department_code == data["department_code"]
            )
            .first()
        )

        if not existing:
            db.add(Departments(**data))


def seed_roles(db):
    roles = [
        {
            "role_name": "Employee",
            "description": "Standard employee role",
        },
        {
            "role_name": "HR",
            "description": "Human Resources role",
        },
        {
            "role_name": "Approver",
            "description": "Role responsible for approving employee requests",
        },
        {
            "role_name": "Administrator",
            "description": "System administrator role",
        },
    ]

    for data in roles:
        existing = (
            db.query(Roles)
            .filter(Roles.role_name == data["role_name"])
            .first()
        )

        if not existing:
            db.add(Roles(**data))


def seed_permissions(db):
    permissions = [
        {
            "permission_code": "employee.read",
            "description": "View employee information",
        },
        {
            "permission_code": "leave.create",
            "description": "Create leave requests",
        },
        {
            "permission_code": "leave.read",
            "description": "View leave requests and balances",
        },
        {
            "permission_code": "leave.approve",
            "description": "Approve or reject leave requests",
        },
        {
            "permission_code": "document.request",
            "description": "Request HR documents",
        },
        {
            "permission_code": "document.process",
            "description": "Process HR document requests",
        },
        {
            "permission_code": "timesheet.submit",
            "description": "Submit timesheets",
        },
        {
            "permission_code": "timesheet.approve",
            "description": "Approve or reject timesheets",
        },
    ]

    for data in permissions:
        existing = (
            db.query(Permissions)
            .filter(
                Permissions.permission_code == data["permission_code"]
            )
            .first()
        )

        if not existing:
            db.add(Permissions(**data))

def seed_employee_and_user(db):
    department = (
        db.query(Departments)
        .filter(Departments.department_code == "IT")
        .first()
    )

    if not department:
        raise ValueError("IT department not found.")

    employee = (
        db.query(Employees)
        .filter(Employees.employee_code == "EMP001")
        .first()
    )

    if not employee:
        employee = Employees(
            employee_code="EMP001",
            employee_name="Test Employee",
            email="employee@test.com",
            department_id=department.department_id,
            job_title="Data Analyst",
            is_active=True,
        )

        db.add(employee)
        db.flush()

    user = (
        db.query(Users)
        .filter(Users.employee_id == employee.employee_id)
        .first()
    )

    if not user:
        user = Users(
            employee_id=employee.employee_id,
            password_hash=hash_password("Test@12345"),
            is_active=True,
        )

        db.add(user)

def seed_database():
    db = SessionLocal()

    try:
        seed_departments(db)
        seed_roles(db)
        seed_permissions(db)
        seed_employee_and_user(db)

        db.commit()

        print("Initial seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print("Error while seeding database:")
        print(e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()