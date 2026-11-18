from sqlalchemy.orm import Session

from app.services.employee_service import get_my_employee_details
from app.services.leave_service import get_my_leave_balance


def execute_tool(
    function_name: str,
    args: dict,
    db: Session,
    current_user
):

    if function_name == "get_my_employee_details":

        result = get_my_employee_details(
            db=db,
            current_user=current_user
        )

    elif function_name == "get_leave_balance":

        balance_year = args.get("balance_year")

        result = get_my_leave_balance(
            db=db,
            current_user=current_user,
            balance_year=balance_year
        )

    else:
        raise ValueError(
            f"Unknown function requested by Gemini: {function_name}"
        )

    # Gemini function responses must be dictionaries
    if isinstance(result, dict):
        return result

    return {"result": result}