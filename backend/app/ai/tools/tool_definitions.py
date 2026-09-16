PORTFOLIO_TOOL = {
    "name": "get_portfolio_summary",
    "description": (
        "Get the authenticated user's portfolio "
        "investment, current value, profit or loss, "
        "return percentage, and holding count."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "portfolio_id": {
                "type": "integer",
                "description": "The portfolio ID to analyze.",
            }
        },
        "required": ["portfolio_id"],
    },
}


ANALYTICS_TOOL = {
    "name": "get_sector_allocation",
    "description": (
        "Get sector-wise investment allocation "
        "for a portfolio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "portfolio_id": {
                "type": "integer",
                "description": "The portfolio ID.",
            }
        },
        "required": ["portfolio_id"],
    },
}


MARKET_TOOL = {
    "name": "get_market_data",
    "description": (
        "Get current and recent market information "
        "for a stock including current price, "
        "previous close, day high, day low, "
        "52-week high and low, volume, market cap, "
        "PE ratio and dividend yield."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": (
                    "Stock ticker such as TCS, INFY "
                    "or RELIANCE."
                ),
            }
        },
        "required": ["ticker"],
    },
}