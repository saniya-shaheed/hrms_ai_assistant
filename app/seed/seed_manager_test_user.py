from app.database import SessionLocal

from app.models.departments import Departments
from app.models.employees import Employees
from app.models.users import Users
from app.models.roles import Roles
from app.models.user_roles import UserRoles

from app.core.security import hash_password


def seed_manager_test_user():
    db = SessionLocal()

    try:
        # Get IT department
        department = (
            db.query(Departments)
            .filter(Departments.department_code == "IT")
            .first()
        )

        # Get Manager role
        manager_role = (
            db.query(Roles)
            .filter(Roles.role_name == "Manager")
            .first()
        )

        if not department or not manager_role:
            raise ValueError("IT department or Manager role not found")

        # Create manager employee
        manager = (
            db.query(Employees)
            .filter(Employees.employee_code == "EMP003")
            .first()
        )

        if not manager:
            manager = Employees(
                employee_code="EMP003",
                employee_name="Test Manager",
                email="manager@test.com",
                department_id=department.department_id,
                job_title="IT Manager",
                is_active=True
            )
            db.add(manager)
            db.flush()

        # Create login user
        user = (
            db.query(Users)
            .filter(Users.employee_id == manager.employee_id)
            .first()
        )

        if not user:
            user = Users(
                employee_id=manager.employee_id,
                password_hash=hash_password("Manager@12345"),
                is_active=True
            )
            db.add(user)
            db.flush()

        # Assign Manager role
        assignment = (
            db.query(UserRoles)
            .filter(
                UserRoles.user_id == user.user_id,
                UserRoles.role_id == manager_role.role_id
            )
            .first()
        )

        if not assignment:
            db.add(
                UserRoles(
                    user_id=user.user_id,
                    role_id=manager_role.role_id
                )
            )

        # Assign EMP001 as a direct report
        employee = (
            db.query(Employees)
            .filter(Employees.employee_code == "EMP001")
            .first()
        )

        if not employee:
            raise ValueError("Test employee EMP001 not found")

        employee.manager_employee_id = manager.employee_id

        db.commit()

        print("Manager test user configured successfully.")
        print("Email: manager@test.com")
        print("Password: Manager@12345")

    except Exception as e:
        db.rollback()
        print("Error creating Manager test user:", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_manager_test_user()