from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    message: str
    data: DataT


class ErrorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class APIErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = False
    message: str
    error: ErrorInfo

