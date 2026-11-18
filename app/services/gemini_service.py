import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.ai.tools.definitions import employee_tools, leave_tools
from app.ai.tool_dispatcher import execute_tool

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

        self.tools = employee_tools + leave_tools

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
                tools=self.tools
            )
        )

        # Check whether Gemini requested one or more function calls
        if response.function_calls:

            if db is None or current_user is None:
                raise ValueError(
                    "Database session and authenticated user "
                    "are required for employee tools."
                )

            # Add Gemini's function-call message
            contents.append(
                response.candidates[0].content
            )

            function_response_parts = []

            for function_call in response.function_calls:

                function_name = function_call.name
                args = function_call.args or {}

                # Execute the requested backend tool
                result = execute_tool(
                    function_name=function_name,
                    args=args,
                    db=db,
                    current_user=current_user
                )

                # Add function result
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response=result
                    )
                )

            # Add all function results in a single user turn
            contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts
                )
            )

            # Ask Gemini to generate the final response
            final_response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=self.tools
                )
            )

            return final_response.text or ""

        return response.text or ""