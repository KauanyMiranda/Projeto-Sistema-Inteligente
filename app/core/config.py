from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sistema Inteligente de Separacao Logistica"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    QR_VERSION: int = 1
    QR_BOX_SIZE: int = 10
    QR_BORDER: int = 4
    QR_FILL_COLOR: str = "black"
    QR_BACK_COLOR: str = "white"

    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_CONTENT_TYPES: list[str] = Field(
        default_factory=lambda: ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("ALLOWED_IMAGE_CONTENT_TYPES", mode="before")
    @classmethod
    def parse_allowed_image_content_types(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def allowed_image_types_normalized(self) -> set[str]:
        return {content_type.lower() for content_type in self.ALLOWED_IMAGE_CONTENT_TYPES}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

