from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.system import HealthData
from app.utils.response import success_response

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=APIResponse[HealthData], summary="Healthcheck da API")
def healthcheck() -> APIResponse[HealthData]:
    data = HealthData(status="ok", timestamp=datetime.now(timezone.utc))
    return success_response(message="Servico operacional.", data=data)

