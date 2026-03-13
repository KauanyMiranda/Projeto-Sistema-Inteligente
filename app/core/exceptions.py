from typing import Any


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class InvalidImageException(AppException):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            status_code=400,
            code="INVALID_IMAGE",
            message=message,
            details=details,
        )


class QRCodeNotFoundException(AppException):
    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            status_code=404,
            code="QRCODE_NOT_FOUND",
            message="Nenhum QR Code foi encontrado na imagem enviada.",
            details=details,
        )


class QRCodeMalformedException(AppException):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            status_code=422,
            code="QRCODE_MALFORMED",
            message=message,
            details=details,
        )

