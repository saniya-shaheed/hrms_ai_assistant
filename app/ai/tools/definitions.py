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