from app.schemas.common import SuccessResponse


def success_response(
    message: str,
    data=None,
) -> SuccessResponse:
    return SuccessResponse(
        message=message,
        data=data,
    )