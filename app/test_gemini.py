# print("STEP 1: Script started")

# import os
# print("STEP 2: os imported")

# from dotenv import load_dotenv
# print("STEP 3: dotenv imported")

# from google import genai
# print("STEP 4: google.genai imported")

# load_dotenv()
# print("STEP 5: .env loaded")

# api_key = os.getenv("GEMINI_API_KEY")
# model_name = os.getenv("GEMINI_MODEL")

# print("API key found:", bool(api_key))
# print("Model:", model_name)

# if not api_key:
#     raise ValueError("GEMINI_API_KEY is not set")

# if not model_name:
#     raise ValueError("GEMINI_MODEL is not set")

# print("STEP 6: Creating Gemini client")

# client = genai.Client(api_key=api_key)

# print("STEP 7: Sending request to Gemini")

# response = client.models.generate_content(
#     model=model_name,
#     contents="Explain what an HRMS is in one simple sentence."
# )

# print("STEP 8: Response received")

# print("Model:", model_name)
# print("Response:")
# print(response.text)

# print("STEP 9: Script finished")

from services.gemini_service import GeminiService


gemini = GeminiService()

response = gemini.generate_response(
    "What is an HRMS? Explain in one simple sentence."
)

print("Gemini response:")
print(response)