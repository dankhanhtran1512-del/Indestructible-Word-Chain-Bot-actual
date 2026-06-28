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

            print("\n========== GEMINI RAW RESPONSE ==========")

            if hasattr(response, "text"):
                print(response.text)
            else:
                print(response)

            print("=========================================\n")

            text = getattr(response, "text", "")

            if not text:
                return {
                    "success": False,
                    "error": "Gemini returned an empty response."
                }

            return self.parse_json_response(text)

        except Exception as error:
            print("\n========== GEMINI EXCEPTION ==========")
            print(type(error).__name__)
            print(error)
            print("======================================\n")

            return {
                "success": False,
                "error": str(error)
            }

    def parse_json_response(self, text):
        try:
            text = text.strip()

            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

            try:
                result = json.loads(text)

            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", text, re.DOTALL)

                if not match:
                    print("\n========== PARSE FAILED ==========")
                    print(text)
                    print("=================================\n")

                    return {
                        "success": False,
                        "error": "AI response could not be parsed."
                    }

                result = json.loads(match.group())

            if isinstance(result, dict):
                result["success"] = True
                return result

            return {
                "success": False,
                "error": "AI response was not a JSON object."
            }

        except Exception as error:
            print("\n========== JSON ERROR ==========")
            print(error)
            print(text)
            print("================================\n")

            return {
                "success": False,
                "error": "AI response could not be parsed."
            }