from google.genai import types


employee_tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_my_employee_details",
                description=(
                    "Retrieve the authenticated employee's own "
                    "employee details, such as employee code, name, "
                    "email, department, job title and hire date. "
                    "This function does not retrieve other employees' details."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={},
                )
            )
        ]
    )
]

leave_tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_leave_balance",
                description=(
                    "Retrieve the authenticated employee's own leave balances. "
                    "The employee can optionally request balances for a specific year. "
                    "This function does not retrieve another employee's leave balance."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "balance_year": types.Schema(
                            type=types.Type.INTEGER,
                            description=(
                                "The leave balance year to retrieve. "
                                "If omitted, balances for all available years are returned."
                            )
                        )
                    }
                )
            ),

            types.FunctionDeclaration(
                name="get_my_leave_requests",
                description=(
                    "Retrieve the authenticated employee's own leave requests. "
                    "This function returns the employee's submitted leave requests "
                    "including leave type, dates, requested days, reason and status. "
                    "This function does not retrieve another employee's leave requests."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
            types.FunctionDeclaration(
                name="submit_leave_request",
                description=(
                    "Submit a new leave request for the authenticated employee. "
                    "The employee must provide the leave type, start date, and end date. "
                    "A reason is optional. The backend validates the leave type, "
                    "working days, notice period, maximum consecutive days, overlapping "
                    "requests, leave balance, and approval rules. "
                    "This function can only submit a leave request for the authenticated employee."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "leave_type_code": types.Schema(
                            type=types.Type.STRING,
                            description=(
                                "The leave type code, for example ANNUAL, SICK, "
                                "CASUAL, or UNPAID."
                            )
                        ),
                        "start_date": types.Schema(
                            type=types.Type.STRING,
                            description=(
                                "The first day of leave in YYYY-MM-DD format."
                            )
                        ),
                        "end_date": types.Schema(
                            type=types.Type.STRING,
                            description=(
                                "The last day of leave in YYYY-MM-DD format."
                            )
                        ),
                        "reason": types.Schema(
                            type=types.Type.STRING,
                            description="Optional reason for the leave request."
                        )
                    },
                    required=[
                        "leave_type_code",
                        "start_date",
                        "end_date"
                    ]
                )
            )
        ]
    )
]