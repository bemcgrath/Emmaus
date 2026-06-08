from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from emmaus.api.deps import get_container
from emmaus.core.bootstrap import Container


router = APIRouter(prefix="/topics", tags=["topics"])
books_router = APIRouter(prefix="/books", tags=["books"])


@router.get("/sources")
def list_sources(container: Container = Depends(get_container)):
    return container.topic_service.list_sources()


@router.get("")
def list_topics(
    source: str = Query(..., description="Topic source: 'openbible' or 'naves'"),
    q: str | None = Query(None, description="Search filter (case-insensitive substring)"),
    limit: int = Query(50, ge=1, le=500),
    container: Container = Depends(get_container),
):
    try:
        return container.topic_service.list_topics(source, query=q, limit=limit)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{source}/{topic_id}/verses")
def get_topic_verses(
    source: str,
    topic_id: str,
    container: Container = Depends(get_container),
):
    try:
        return container.topic_service.get_topic_verses(source, topic_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@books_router.get("")
def list_books(container: Container = Depends(get_container)):
    try:
        return container.topic_service.list_books()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
