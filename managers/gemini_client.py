import json

from google import genai
from config import GEMINI_API_KEY


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def ask(self, prompt):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            return self.parse_json_response(response.text)

        except Exception as error:
            return {
                "success": False,
                "error": str(error)
            }

    def parse_json_response(self, text):
        try:
            text = text.strip()
            text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)

            if isinstance(result, dict):
                result["success"] = True
                return result

            return {
                "success": False,
                "error": "AI response was not a JSON object."
            }

        except Exception:
            return {
                "success": False,
                "error": "AI response could not be parsed."
            }