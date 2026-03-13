from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item import ItemBase, ItemData
from app.schemas.sort import SortDecision


class GenerateQRCodeRequest(ItemBase):
    nome_arquivo: str | None = Field(
        default=None,
        max_length=120,
        pattern=r"^[A-Za-z0-9._-]+$",
        description="Nome opcional para referencia do QR Code gerado (sem caminhos).",
    )


class GenerateQRCodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: ItemData
    filename: str
    mime_type: str = "image/png"
    payload_json: str
    qr_code_base64: str
    sort_preview: SortDecision


class ReadQRCodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: ItemData
    raw_payload: str
    sort_preview: SortDecision

