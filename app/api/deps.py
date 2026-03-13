from functools import lru_cache

from app.services.qrcode_service import QRCodeService
from app.services.sorter_service import SorterService


@lru_cache
def get_sorter_service() -> SorterService:
    return SorterService()


@lru_cache
def get_qrcode_service() -> QRCodeService:
    return QRCodeService(sorter_service=get_sorter_service())

