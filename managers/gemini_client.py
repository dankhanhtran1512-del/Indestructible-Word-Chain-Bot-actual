import json
import logging
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

            text = getattr(response, "text", "")

            logging.warning("Gemini raw response: %s", text)

            if not text:
                return {
                    "success": False,
                    "error": "Gemini returned an empty response."
                }

            return self.parse_json_response(text)

        except Exception as error:
            logging.exception("Gemini exception")

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
                    logging.error("Gemini JSON parse failed. Raw response: %s", text)
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
            logging.exception("Gemini JSON parsing exception")

            return {
                "success": False,
                "error": str(error)
            }