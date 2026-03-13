from app.schemas.common import APIResponse, DataT


def success_response(*, message: str, data: DataT) -> APIResponse[DataT]:
    return APIResponse[DataT](success=True, message=message, data=data)

