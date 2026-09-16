import json

from app.services.gemini_service import GeminiService


class ToolSelector:

    def __init__(
        self,
        gemini_service: GeminiService,
    ):
        self.gemini_service = gemini_service

    async def select_tool(
        self,
        message: str,
    ) -> dict:

        prompt = f"""
You are the tool-selection component of FinGenie.

Available tools:

1. portfolio
   Use when the user asks about:
   - portfolio performance
   - total investment
   - current portfolio value
   - profit or loss
   - portfolio returns

2. analytics
   Use when the user asks about:
   - sector allocation
   - diversification
   - concentration
   - portfolio exposure

3. market
   Use when the user asks about:
   - stock price
   - market price
   - 52-week high or low
   - market capitalization
   - trading volume
   - PE ratio
   - dividend information

4. general
   Use when the question does not require
   portfolio or market data.

Return ONLY valid JSON.

For portfolio:
{{
    "tool": "portfolio"
}}

For analytics:
{{
    "tool": "analytics"
}}

For market:
{{
    "tool": "market",
    "ticker": "TCS"
}}

For general:
{{
    "tool": "general"
}}

User message:
{message}
"""

        response = await self.gemini_service.generate_response(
            prompt
        )

        return self._parse_response(response)

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict:

        response = response.strip()

        if response.startswith("```"):
            response = response.replace(
                "```json",
                "",
            ).replace(
                "```",
                "",
            ).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "tool": "general",
            }