from fastapi import APIRouter, Depends

from emmaus.api.deps import get_container
from emmaus.api.schemas import RegisterApiTextSourceRequest, RegisterLocalTextSourceRequest
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/sources/text", tags=["text-sources"])


@router.get("")
def list_text_sources(container: Container = Depends(get_container)):
    return {"items": container.text_service.list_sources()}


@router.post("/local", status_code=201)
def register_local_text_source(
    payload: RegisterLocalTextSourceRequest,
    container: Container = Depends(get_container),
):
    descriptor = container.text_service.register_local_source(
        source_id=payload.source_id,
        name=payload.name,
        file_path=payload.file_path,
        license_name=payload.license_name,
    )
    return descriptor


@router.post("/api", status_code=201)
def register_api_text_source(
    payload: RegisterApiTextSourceRequest,
    container: Container = Depends(get_container),
):
    descriptor = container.text_service.register_api_source(
        source_id=payload.source_id,
        name=payload.name,
        base_url=str(payload.base_url),
        api_key=payload.api_key,
        license_name=payload.license_name,
    )
    return descriptor
