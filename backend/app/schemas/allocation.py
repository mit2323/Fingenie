from pydantic import BaseModel


class SectorAllocationResponse(BaseModel):

    sector: str

    investment: float

    percentage: float