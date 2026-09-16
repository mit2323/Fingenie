class RiskTool:

    def __init__(
        self,
        risk_analysis_service,
    ):
        self.risk_analysis_service = (
            risk_analysis_service
        )

    async def execute(
        self,
        portfolio_id: int,
        user_id: int,
    ):

        return await (
            self.risk_analysis_service.analyze(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )