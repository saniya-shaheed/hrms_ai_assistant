# Access & Control
from app.models.departments import Departments
from app.models.employees import Employees
from app.models.users import Users
from app.models.roles import Roles
from app.models.permissions import Permissions
from app.models.user_roles import UserRoles
from app.models.role_permissions import RolePermissions
from app.models.audit_logs import AuditLogs

# Leave Management
from app.models.leave_types import LeaveTypes
from app.models.leave_entitlement_rules import LeaveEntitlementRules
from app.models.leave_balances import LeaveBalances
from app.models.leave_requests import LeaveRequests
from app.models.leave_approvals import LeaveApprovals
from app.models.leave_transactions import LeaveTransactions
from app.models.public_holidays import PublicHolidays

# HR Document Management
from app.models.hr_document_types import HRDocumentTypes
from app.models.hr_document_requests import HRDocumentRequests
from app.models.hr_document_request_history import HRDocumentRequestHistory

# Timesheet Management
from app.models.timesheets import Timesheets
from app.models.timesheet_entries import TimesheetEntries
from app.models.timesheet_approvals import TimesheetApprovals

# AI Assistant & Conversation
from app.models.ai_conversations import AIConversations
from app.models.ai_messages import AIMessages
from app.models.ai_tool_executions import AIToolExecutions  

# HR Policies Knowledge Base
from app.models.hr_policies import HRPolicies 
from app.models.hr_policy_versions import HRPolicyVersions
from app.models.hr_policy_chunks import HRPolicyChunks





