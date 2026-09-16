class RiskAnalysisService:

    def __init__(
        self,
        allocation_service,
    ):
        self.allocation_service = allocation_service

    async def analyze(
        self,
        portfolio_id: int,
        user_id: int,
    ) -> dict:

        allocations = (
            await self.allocation_service
            .get_sector_allocation(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if not allocations:

            return {
                "risk_level": "Unknown",
                "largest_sector": None,
                "largest_sector_percentage": 0.0,
                "message": (
                    "No sector allocation data "
                    "is available."
                ),
            }

        # --------------------------------
        # Find largest sector
        # --------------------------------

        largest_sector = max(
            allocations,
            key=lambda item: item.percentage,
        )

        percentage = float(
            largest_sector.percentage
        )

        # --------------------------------
        # Simple concentration levels
        # --------------------------------

        if percentage >= 60:

            risk_level = "High"

        elif percentage >= 40:

            risk_level = "Moderate"

        else:

            risk_level = "Low"

        # --------------------------------
        # Result
        # --------------------------------

        return {
            "risk_level": risk_level,
            "largest_sector": (
                largest_sector.sector
            ),
            "largest_sector_percentage": round(
                percentage,
                2,
            ),
            "message": (
                f"The largest sector is "
                f"{largest_sector.sector}, "
                f"representing {percentage:.2f}% "
                f"of the portfolio."
            ),
        }