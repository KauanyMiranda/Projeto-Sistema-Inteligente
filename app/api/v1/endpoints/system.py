from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import APIResponse
from app.schemas.item import RegionEnum
from app.schemas.system import ApiV1Data, ConfigData, RegionsData
from app.utils.response import success_response

router = APIRouter(tags=["System"])


@router.get("", response_model=APIResponse[ApiV1Data], summary="Status da API v1")
def api_v1_status() -> APIResponse[ApiV1Data]:
    data = ApiV1Data(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        api_prefix=settings.API_V1_PREFIX,
    )
    return success_response(message="API v1 ativa.", data=data)


@router.get(
    "/regions",
    response_model=APIResponse[RegionsData],
    summary="Listar regioes de destino aceitas",
)
def list_regions() -> APIResponse[RegionsData]:
    data = RegionsData(regions=[region for region in RegionEnum])
    return success_response(message="Lista de regioes retornada.", data=data)


@router.get(
    "/config",
    response_model=APIResponse[ConfigData],
    summary="Exibir configuracoes basicas da API",
)
def get_config() -> APIResponse[ConfigData]:
    data = ConfigData(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        api_prefix=settings.API_V1_PREFIX,
        max_upload_size_mb=settings.MAX_UPLOAD_SIZE_MB,
        allowed_image_content_types=sorted(settings.allowed_image_types_normalized),
        qr_code_defaults={
            "version": settings.QR_VERSION,
            "box_size": settings.QR_BOX_SIZE,
            "border": settings.QR_BORDER,
            "fill_color": settings.QR_FILL_COLOR,
            "back_color": settings.QR_BACK_COLOR,
        },
    )
    return success_response(message="Configuracoes carregadas.", data=data)

