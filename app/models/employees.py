from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Employees(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, nullable=False, primary_key=True, index=True)
    employee__code = Column(String(50), nullable=False, unique=True, index=True)
    employee_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), index=True)
    job_title = Column(String(100))
    hire_date = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)
    manager_employee_id = Column(Integer, ForeignKey("employees.employee_id"), index=True)


    department = relationship("Departments", back_populates="employees")
    manager = relationship("Employees",remote_side=[employee_id],back_populates="subordinates")
    subordinates = relationship("Employees",back_populates="manager")
    user = relationship("Employees", back_populates="employee")
    leave_balances = relationship("LeaveBalances", back_populates="employee")
    leave_requests = relationship("LeaveRequests", back_populates="employee")
    leave_approvals = relationship("LeaveApprovals", back_populates="approver")
    leave_transactions = relationship("LeaveTransactions", back_populates="employee")
    hr_document_requests = relationship("HRDocumentRequests", back_populates="employee")
    time_sheets = relationship("TimeSheets", back_populates="employee")
    timesheet_approvals = relationship("TimesheetApprovals", back_populates="approver_employee")