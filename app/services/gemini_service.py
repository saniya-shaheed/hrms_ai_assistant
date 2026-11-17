import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.ai.tools.definitions import employee_tools
from app.services.employee_service import get_my_employee_details

load_dotenv()


class GeminiService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        if not model_name:
            raise ValueError("GEMINI_MODEL is not configured")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_response(
        self,
        message: str,
        history: list[dict] | None = None,
        db: Session | None = None,
        current_user=None
    ) -> str:

        contents = []

        if history:
            contents.extend(history)

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(text=message)
                ]
            )
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=employee_tools
            )
        )

        # Check whether Gemini requested a function call
        if response.function_calls:

            function_call = response.function_calls[0]

            function_name = function_call.name

            if function_name == "get_my_employee_details":

                if db is None or current_user is None:
                    raise ValueError(
                        "Database session and authenticated user "
                        "are required for employee tools."
                    )

                result = get_my_employee_details(
                    db=db,
                    current_user=current_user
                )

            else:
                raise ValueError(
                    f"Unknown function requested by Gemini: "
                    f"{function_name}"
                )

            # Add Gemini's function-call message to the conversation
            contents.append(
                response.candidates[0].content
            )

            # Add the function result
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=function_name,
                            response=result
                        )
                    ]
                )
            )

            # Ask Gemini to generate the final natural-language response
            final_response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=employee_tools
                )
            )

            return final_response.text

        return response.text