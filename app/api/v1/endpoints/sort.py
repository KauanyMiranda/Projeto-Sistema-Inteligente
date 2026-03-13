from fastapi import APIRouter, Depends

from app.api.deps import get_sorter_service
from app.schemas.common import APIResponse
from app.schemas.sort import SortPreviewRequest, SortPreviewResponse
from app.services.sorter_service import SorterService
from app.utils.response import success_response

router = APIRouter(prefix="/sort", tags=["Sorting"])


@router.post(
    "/preview",
    response_model=APIResponse[SortPreviewResponse],
    summary="Simular decisao de separacao logistica",
)
def preview_sort(
    payload: SortPreviewRequest,
    service: SorterService = Depends(get_sorter_service),
) -> APIResponse[SortPreviewResponse]:
    item = payload.to_item_data()
    decision = service.preview_sort(item=item)
    data = SortPreviewResponse(item=item, decision=decision)
    return success_response(message="Simulacao de separacao gerada.", data=data)

