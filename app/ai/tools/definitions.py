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
            )
        ]
    )
]