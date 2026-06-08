from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from emmaus.api.deps import get_container
from emmaus.core.bootstrap import Container
from emmaus.domain.models import PassageReference


router = APIRouter(prefix="/memorization", tags=["memorization"])


class AddVerseRequest(BaseModel):
    user_id: str
    book: str
    chapter: int
    start_verse: int
    end_verse: int | None = None

    def to_reference(self) -> PassageReference:
        return PassageReference(
            book=self.book,
            chapter=self.chapter,
            start_verse=self.start_verse,
            end_verse=self.end_verse,
        )


class ReviewRequest(BaseModel):
    rating: Literal["again", "hard", "good", "easy"]
    drill_stage: int = Field(default=0, ge=0, le=4)


class DrillAttemptRequest(BaseModel):
    typed_text: str = Field(default="")


class TargetRequest(BaseModel):
    title: str = Field(min_length=1)
    verse_count_goal: int = Field(ge=1)
    target_date: date


@router.post("/verses")
def add_verse(payload: AddVerseRequest, container: Container = Depends(get_container)):
    try:
        verse = container.memorization_service.add_verse(payload.user_id, payload.to_reference())
    except LookupError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return verse


@router.get("/{user_id}/verses")
def list_verses(user_id: str, container: Container = Depends(get_container)):
    return container.memorization_service.list_verses(user_id)


@router.get("/{user_id}/queue")
def list_queue(user_id: str, container: Container = Depends(get_container)):
    return container.memorization_service.list_due_today(user_id)


@router.get("/{user_id}/progress")
def get_progress(user_id: str, container: Container = Depends(get_container)):
    return container.memorization_service.build_progress(user_id)


@router.post("/verses/{verse_id}/drill-attempt")
def submit_drill_attempt(
    verse_id: str,
    payload: DrillAttemptRequest,
    container: Container = Depends(get_container),
):
    try:
        result = container.memorization_service.submit_drill_attempt(verse_id, payload.typed_text)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    progress = container.memorization_service.build_progress(result.verse.user_id)
    return {"result": result, "progress": progress}


@router.post("/verses/{verse_id}/review")
def record_review(
    verse_id: str,
    payload: ReviewRequest,
    container: Container = Depends(get_container),
):
    try:
        verse = container.memorization_service.apply_review(verse_id, payload.rating, payload.drill_stage)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    progress = container.memorization_service.build_progress(verse.user_id)
    return {"verse": verse, "progress": progress}


@router.delete("/verses/{verse_id}")
def delete_verse(verse_id: str, container: Container = Depends(get_container)):
    container.memorization_service.delete_verse(verse_id)
    return {"status": "deleted"}


@router.post("/{user_id}/targets")
def create_target(
    user_id: str,
    payload: TargetRequest,
    container: Container = Depends(get_container),
):
    return container.memorization_service.set_target(
        user_id=user_id,
        title=payload.title,
        verse_count_goal=payload.verse_count_goal,
        target_date=payload.target_date,
    )


@router.get("/{user_id}/targets")
def list_targets(user_id: str, container: Container = Depends(get_container)):
    return container.memorization_service.list_targets(user_id)
