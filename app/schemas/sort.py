from pydantic import BaseModel, ConfigDict

from app.schemas.item import ItemBase, ItemData, RegionEnum


class SortDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    region: RegionEnum
    gate: str
    actuator_command: str
    message: str


class SortPreviewRequest(ItemBase):
    pass


class SortPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: ItemData
    decision: SortDecision

