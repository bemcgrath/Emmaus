from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import PassageQuery
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/texts", tags=["texts"])


@router.post("/passage")
def get_passage(payload: PassageQuery, container: Container = Depends(get_container)):
    passage = container.text_service.get_passage(payload.to_reference(), payload.source_id)
    return passage
