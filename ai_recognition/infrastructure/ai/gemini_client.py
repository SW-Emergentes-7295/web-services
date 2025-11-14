from google import genai
import os

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("API_KEY_GEMINI")
        if not api_key:
            raise ValueError("API_KEY_GEMINI environment variable not set")

        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"text": "You are a helpful visual assistant, you need to respond to the user's voice command accordingly in your language."},
                        {"text": prompt}
                    ]
                }
            ]
        )

        return response.text if response else ""