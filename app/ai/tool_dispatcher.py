from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.employee_service import get_my_employee_details
from app.services.leave_service import get_my_leave_balance
from app.services.leave_request_service import (
    get_my_leave_requests,
    submit_leave_request_from_ai
)


def execute_tool(
    function_name: str,
    args: dict,
    db: Session,
    current_user
):

    try:

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

        elif function_name == "get_my_leave_requests":

            result = get_my_leave_requests(
                db=db,
                current_user=current_user
            )

        elif function_name == "submit_leave_request":

            result = submit_leave_request_from_ai(
                db=db,
                current_user=current_user,
                leave_type_code=args.get("leave_type_code"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                reason=args.get("reason")
            )

        else:
            raise ValueError(
                f"Unknown function requested by Gemini: {function_name}"
            )

        if isinstance(result, dict):
            return result

        return {"result": result}

    except HTTPException as e:

        return {
            "success": False,
            "status_code": e.status_code,
            "error": e.detail
        }