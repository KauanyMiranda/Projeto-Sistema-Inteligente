from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_BRAZILIAN_UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


class RegionEnum(str, Enum):
    NORTE = "NORTE"
    NORDESTE = "NORDESTE"
    CENTRO_OESTE = "CENTRO-OESTE"
    SUDESTE = "SUDESTE"
    SUL = "SUL"


class ItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id_item: str = Field(..., min_length=1, max_length=64, examples=["ITEM-0001"])
    descricao: str = Field(..., min_length=1, max_length=200)
    regiao_destino: RegionEnum
    uf_destino: str = Field(..., min_length=2, max_length=2, examples=["RO"])
    cidade_destino: str = Field(..., min_length=1, max_length=120)
    timestamp_criacao: datetime | None = Field(
        default=None,
        description="Data/hora de criacao do item. Se omitida, sera preenchida com UTC atual.",
    )

    @field_validator("uf_destino")
    @classmethod
    def validate_uf(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_BRAZILIAN_UFS:
            raise ValueError("uf_destino deve ser uma UF valida do Brasil.")
        return normalized

    @field_validator("cidade_destino")
    @classmethod
    def normalize_city(cls, value: str) -> str:
        return value.strip()

    def to_item_data(self) -> "ItemData":
        timestamp = self.timestamp_criacao or datetime.now(timezone.utc)
        return ItemData(
            id_item=self.id_item,
            descricao=self.descricao,
            regiao_destino=self.regiao_destino,
            uf_destino=self.uf_destino,
            cidade_destino=self.cidade_destino,
            timestamp_criacao=timestamp,
        )


class ItemData(ItemBase):
    timestamp_criacao: datetime

