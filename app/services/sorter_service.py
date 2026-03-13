from app.core.exceptions import QRCodeMalformedException
from app.schemas.item import ItemData, RegionEnum
from app.schemas.sort import SortDecision


REGION_SORT_RULES: dict[RegionEnum, dict[str, str]] = {
    RegionEnum.NORTE: {
        "gate": "GATE_NORTE",
        "actuator_command": "DIVERT_LEFT_01",
        "message": "Direcionar item para canal de expedicao da regiao Norte.",
    },
    RegionEnum.NORDESTE: {
        "gate": "GATE_NORDESTE",
        "actuator_command": "DIVERT_LEFT_02",
        "message": "Direcionar item para canal de expedicao da regiao Nordeste.",
    },
    RegionEnum.CENTRO_OESTE: {
        "gate": "GATE_CENTRO_OESTE",
        "actuator_command": "DIVERT_CENTER_01",
        "message": "Direcionar item para canal de expedicao da regiao Centro-Oeste.",
    },
    RegionEnum.SUDESTE: {
        "gate": "GATE_SUDESTE",
        "actuator_command": "DIVERT_RIGHT_01",
        "message": "Direcionar item para canal de expedicao da regiao Sudeste.",
    },
    RegionEnum.SUL: {
        "gate": "GATE_SUL",
        "actuator_command": "DIVERT_RIGHT_02",
        "message": "Direcionar item para canal de expedicao da regiao Sul.",
    },
}


class SorterService:
    def preview_sort(self, item: ItemData) -> SortDecision:
        rule = REGION_SORT_RULES.get(item.regiao_destino)
        if rule is None:
            raise QRCodeMalformedException(
                message="Regiao de destino nao suportada para separacao.",
                details={"regiao": str(item.regiao_destino)},
            )

        return SortDecision(
            item_id=item.id_item,
            region=item.regiao_destino,
            gate=rule["gate"],
            actuator_command=rule["actuator_command"],
            message=rule["message"],
        )

