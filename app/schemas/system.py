from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.item import RegionEnum


class RootData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    version: str
    environment: str
    api_prefix: str


class ApiV1Data(RootData):
    pass


class HealthData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    timestamp: datetime


class RegionsData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    regions: list[RegionEnum]


class ConfigData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    app_version: str
    environment: str
    api_prefix: str
    max_upload_size_mb: int
    allowed_image_content_types: list[str]
    qr_code_defaults: dict[str, str | int]

