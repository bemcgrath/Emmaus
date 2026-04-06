from fastapi import APIRouter, Depends, HTTPException

from emmaus.api.deps import get_container
from emmaus.api.schemas import (
    RegisterApiTextSourceRequest,
    RegisterESVTextSourceRequest,
    RegisterLocalTextSourceRequest,
    RegisterUploadedTextSourceRequest,
)
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/sources/text", tags=["text-sources"])


@router.get("")
def list_text_sources(container: Container = Depends(get_container)):
    return {"items": container.text_service.list_sources()}


@router.get("/templates")
def list_text_source_templates():
    return {
        "items": [
            {
                "template_id": "starter",
                "name": "Included Starter Bible",
                "setup_mode": "starter",
                "description": "Begin immediately with the Bible already included in Emmaus.",
                "recommended": True,
                "source_id": "sample_local",
            },
            {
                "template_id": "esv",
                "name": "ESV",
                "setup_mode": "esv_api",
                "description": "Connect the official ESV API with your Crossway API key.",
                "recommended": False,
                "source_id": "esv",
            },
            {
                "template_id": "web",
                "name": "WEB",
                "setup_mode": "upload",
                "description": "Upload a public-domain WEB JSON file from this device.",
                "recommended": False,
                "source_id": None,
            },
            {
                "template_id": "kjv",
                "name": "KJV",
                "setup_mode": "upload",
                "description": "Upload a KJV JSON file or connect a source you already have.",
                "recommended": False,
                "source_id": None,
            },
            {
                "template_id": "asv",
                "name": "ASV",
                "setup_mode": "upload",
                "description": "Upload an ASV JSON file from this device.",
                "recommended": False,
                "source_id": None,
            },
            {
                "template_id": "licensed_other",
                "name": "Other licensed translation",
                "setup_mode": "generic_api",
                "description": "Connect another licensed provider such as NIV, NLT, NKJV, NASB, or CSB.",
                "recommended": False,
                "source_id": None,
            },
        ]
    }


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


@router.post("/esv", status_code=201)
def register_esv_text_source(
    payload: RegisterESVTextSourceRequest,
    container: Container = Depends(get_container),
):
    descriptor = container.text_service.register_esv_source(
        api_key=payload.api_key,
        source_id=payload.source_id,
        name=payload.name,
        license_name=payload.license_name,
    )
    return descriptor


@router.post("/upload", status_code=201)
def register_uploaded_text_source(
    payload: RegisterUploadedTextSourceRequest,
    container: Container = Depends(get_container),
):
    try:
        descriptor = container.text_service.register_uploaded_source(
            source_id=payload.source_id,
            name=payload.name,
            filename=payload.filename,
            file_content=payload.file_content,
            license_name=payload.license_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return descriptor
