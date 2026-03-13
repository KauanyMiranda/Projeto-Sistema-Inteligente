import base64
import json
import re
from io import BytesIO

import cv2
import numpy as np
import qrcode
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import (
    InvalidImageException,
    QRCodeMalformedException,
    QRCodeNotFoundException,
)
from app.schemas.item import ItemData
from app.schemas.qrcode import (
    GenerateQRCodeRequest,
    GenerateQRCodeResponse,
    ReadQRCodeResponse,
)
from app.services.sorter_service import SorterService


class QRCodeService:
    def __init__(self, sorter_service: SorterService) -> None:
        self.sorter_service = sorter_service

    def generate_qrcode(self, payload: GenerateQRCodeRequest) -> GenerateQRCodeResponse:
        item = payload.to_item_data()
        serialized_payload = self._serialize_item(item)
        image_bytes = self._build_qr_image(serialized_payload)
        sort_preview = self.sorter_service.preview_sort(item=item)

        filename = payload.nome_arquivo or f"{item.id_item}.png"
        safe_filename = self._sanitize_filename(filename)

        return GenerateQRCodeResponse(
            item=item,
            filename=safe_filename,
            payload_json=serialized_payload,
            qr_code_base64=base64.b64encode(image_bytes).decode("ascii"),
            sort_preview=sort_preview,
        )

    def read_qrcode(self, image_bytes: bytes) -> ReadQRCodeResponse:
        image = self._decode_image_bytes(image_bytes)
        raw_payload = self._detect_qrcode_payload(image)
        item = self._parse_payload_to_item(raw_payload)
        sort_preview = self.sorter_service.preview_sort(item=item)

        return ReadQRCodeResponse(
            item=item,
            raw_payload=raw_payload,
            sort_preview=sort_preview,
        )

    def _serialize_item(self, item: ItemData) -> str:
        return item.model_dump_json()

    def _build_qr_image(self, data: str) -> bytes:
        qr = qrcode.QRCode(
            version=settings.QR_VERSION,
            box_size=settings.QR_BOX_SIZE,
            border=settings.QR_BORDER,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
        )
        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color=settings.QR_FILL_COLOR,
            back_color=settings.QR_BACK_COLOR,
        )
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _decode_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImageException(message="Imagem invalida ou corrompida.")
        return image

    def _detect_qrcode_payload(self, image: np.ndarray) -> str:
        detector = cv2.QRCodeDetector()
        payload, points, _ = detector.detectAndDecode(image)
        if points is None or not payload:
            raise QRCodeNotFoundException()
        return payload.strip()

    def _parse_payload_to_item(self, raw_payload: str) -> ItemData:
        try:
            decoded = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            raise QRCodeMalformedException(
                message="Conteudo do QR Code nao esta em JSON valido.",
                details={"erro_json": str(exc)},
            ) from exc

        if not isinstance(decoded, dict):
            raise QRCodeMalformedException(
                message="Conteudo do QR Code deve ser um objeto JSON.",
                details={"tipo_recebido": type(decoded).__name__},
            )

        try:
            return ItemData.model_validate(decoded)
        except ValidationError as exc:
            raise QRCodeMalformedException(
                message="JSON do QR Code nao corresponde ao schema esperado.",
                details={"campos_invalidos": exc.errors()},
            ) from exc

    def _sanitize_filename(self, filename: str) -> str:
        normalized = filename.strip()
        if not normalized:
            return "qrcode.png"

        normalized = re.sub(r"[^A-Za-z0-9._-]", "_", normalized)
        if not normalized.lower().endswith(".png"):
            normalized = f"{normalized}.png"
        return normalized

