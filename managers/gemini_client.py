import json
import re

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

            text = getattr(response, "text", None)

            if not text:
                return {
                    "success": False,
                    "error": "AI returned an empty response."
                }

            return self.parse_json_response(text)

        except Exception as error:
            print("Gemini error:", error)
            return {
                "success": False,
                "error": str(error)
            }

    def parse_json_response(self, text):
        try:
            text = text.strip()

            text = text.replace("```json", "").replace("```", "").strip()

            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", text, re.DOTALL)

                if not match:
                    return {
                        "success": False,
                        "error": f"AI response could not be parsed. Raw response: {text[:500]}"
                    }

                result = json.loads(match.group(0))

            if isinstance(result, dict):
                result["success"] = True
                return result

            return {
                "success": False,
                "error": "AI response was not a JSON object."
            }

        except Exception as error:
            return {
                "success": False,
                "error": f"AI response could not be parsed: {error}"
            }