from app.database import SessionLocal

from app.models.departments import Departments
from app.models.employees import Employees
from app.models.users import Users
from app.models.roles import Roles
from app.models.user_roles import UserRoles

from app.core.security import hash_password


def seed_admin_test_user():
    db = SessionLocal()

    try:
        # Get HR department
        hr_department = (
            db.query(Departments)
            .filter(Departments.department_code == "HR")
            .first()
        )

        # Get ADMIN role
        hr_role = (
            db.query(Roles)
            .filter(Roles.role_name == "Administrator")
            .first()
        )

        if not hr_department or not hr_role:
            raise ValueError("HR department or role not found")

        # Create admin employee if not already present
        employee = (
            db.query(Employees)
            .filter(Employees.employee_code == "EMP005")
            .first()
        )

        if not employee:
            employee = Employees(
                employee_code="EMP005",
                employee_name="Test Admin User",
                email="admin@test.com",
                department_id=hr_department.department_id,
                job_title="Admin Officer",
                is_active=True
            )

            db.add(employee)
            db.flush()

        # Create login user if not already present
        user = (
            db.query(Users)
            .filter(Users.employee_id == employee.employee_id)
            .first()
        )

        if not user:
            user = Users(
                employee_id=employee.employee_id,
                password_hash=hash_password("admin@12345"),
                is_active=True
            )

            db.add(user)
            db.flush()

        # Assign HR role if not already assigned
        existing_assignment = (
            db.query(UserRoles)
            .filter(
                UserRoles.user_id == user.user_id,
                UserRoles.role_id == hr_role.role_id
            )
            .first()
        )

        if not existing_assignment:
            assignment = UserRoles(
                user_id=user.user_id,
                role_id=hr_role.role_id
            )

            db.add(assignment)

        db.commit()

        print("admin test user created/configured successfully.")
        print("Email: admin@test.com")
        print("Password: admin@12345")

    except Exception as e:
        db.rollback()
        print("Error creating admin test user:", e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_test_user()