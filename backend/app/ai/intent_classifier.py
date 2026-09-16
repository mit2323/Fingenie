class IntentClassifier:

    def classify(
        self,
        message: str,
    ) -> str:

        message = message.lower()

        portfolio_keywords = [
            "portfolio",
            "investment",
            "investments",
            "profit",
            "loss",
            "return",
            "performance",
        ]

        analytics_keywords = [
            "sector",
            "allocation",
            "diversification",
            "exposure",
            "concentration",
        ]

        market_keywords = [
            "price",
            "trading at",
            "quote",
            "market cap",
            "52 week",
            "52-week",
            "volume",
            "pe ratio",
            "p/e",
            "dividend",
            "stock",
            "share price",
        ]

        if any(
            keyword in message
            for keyword in portfolio_keywords
        ):
            return "portfolio"

        if any(
            keyword in message
            for keyword in analytics_keywords
        ):
            return "analytics"

        if any(
            keyword in message
            for keyword in market_keywords
        ):
            return "market"

        return "general"