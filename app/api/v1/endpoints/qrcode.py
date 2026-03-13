from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import get_qrcode_service
from app.core.config import settings
from app.core.exceptions import InvalidImageException
from app.schemas.common import APIResponse
from app.schemas.qrcode import (
    GenerateQRCodeRequest,
    GenerateQRCodeResponse,
    ReadQRCodeResponse,
)
from app.services.qrcode_service import QRCodeService
from app.utils.response import success_response

router = APIRouter(prefix="/qrcode", tags=["QRCode"])


@router.post(
    "/generate",
    response_model=APIResponse[GenerateQRCodeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar QR Code para item logistico",
)
def generate_qrcode(
    payload: GenerateQRCodeRequest,
    service: QRCodeService = Depends(get_qrcode_service),
) -> APIResponse[GenerateQRCodeResponse]:
    result = service.generate_qrcode(payload=payload)
    return success_response(message="QR Code gerado com sucesso.", data=result)


@router.post(
    "/read",
    response_model=APIResponse[ReadQRCodeResponse],
    summary="Ler e decodificar QR Code a partir de imagem",
)
async def read_qrcode(
    file: UploadFile = File(..., description="Imagem contendo um QR Code"),
    service: QRCodeService = Depends(get_qrcode_service),
) -> APIResponse[ReadQRCodeResponse]:
    content_type = (file.content_type or "").lower()
    if content_type not in settings.allowed_image_types_normalized:
        raise InvalidImageException(
            message="Tipo de arquivo nao suportado para leitura de QR Code.",
            details={
                "content_type_recebido": file.content_type,
                "tipos_permitidos": sorted(settings.allowed_image_types_normalized),
            },
        )

    image_bytes = await file.read()
    await file.close()

    if not image_bytes:
        raise InvalidImageException(message="Arquivo de imagem vazio.")

    if len(image_bytes) > settings.max_upload_size_bytes:
        raise InvalidImageException(
            message="Arquivo excede o limite maximo permitido.",
            details={
                "tamanho_bytes": len(image_bytes),
                "limite_bytes": settings.max_upload_size_bytes,
            },
        )

    result = service.read_qrcode(image_bytes=image_bytes)
    return success_response(message="QR Code lido com sucesso.", data=result)

