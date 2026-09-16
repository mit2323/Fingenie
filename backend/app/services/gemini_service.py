import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiService:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "AI service is not configured."
            )



        self.client = genai.Client(
            api_key=api_key,
        )

        # --------------------------------
        # Get model
        # --------------------------------

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

    async def generate_response(
        self,
        prompt: str,
    ) -> str:


        if not prompt or not prompt.strip():

            raise ValueError(
                "Gemini prompt cannot be empty."
            )

        try:
            response = await (
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                    ),
                )
            )

        except Exception as exc:
            print(
                f"Gemini API error: {exc}"
            )

            raise ValueError(
                "AI service is temporarily "
                "unavailable. Please try again later."
            )


        if not response:

            raise ValueError(
                "AI service returned an empty response."
            )

        text = response.text

        if not text or not text.strip():

            raise ValueError(
                "AI service returned an empty response."
            )

        return text.strip()