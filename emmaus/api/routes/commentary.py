from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import PassageQuery
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/commentary", tags=["commentary"])


@router.get("/sources")
def list_commentary_sources(container: Container = Depends(get_container)):
    return {"items": container.commentary_registry.list()}


@router.post("/lookup")
def lookup_commentary(payload: PassageQuery, container: Container = Depends(get_container)):
    source_id = payload.source_id or container.settings.default_commentary_source
    provider = container.commentary_registry.get(source_id)
    return {"items": provider.get_commentary(payload.to_reference())}
