from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from emmaus.api.deps import get_container
from emmaus.core.bootstrap import Container
from emmaus.domain.models import PassageReference


router = APIRouter(prefix="/notes", tags=["notes"])


class CreateNoteRequest(BaseModel):
    user_id: str
    book: str
    chapter: int
    start_verse: int
    end_verse: int | None = None
    title: str | None = None
    body: str = Field(min_length=1)
    session_id: str | None = None

    def to_reference(self) -> PassageReference:
        return PassageReference(
            book=self.book,
            chapter=self.chapter,
            start_verse=self.start_verse,
            end_verse=self.end_verse,
        )


class UpdateNoteRequest(BaseModel):
    title: str | None = None
    body: str | None = None


@router.post("")
def create_note(payload: CreateNoteRequest, container: Container = Depends(get_container)):
    try:
        return container.notes_service.create_note(
            user_id=payload.user_id,
            reference=payload.to_reference(),
            body=payload.body,
            title=payload.title,
            session_id=payload.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{user_id}")
def list_notes(
    user_id: str,
    book: str | None = Query(default=None),
    chapter: int | None = Query(default=None),
    start_verse: int | None = Query(default=None),
    end_verse: int | None = Query(default=None),
    container: Container = Depends(get_container),
):
    reference: PassageReference | None = None
    if book and chapter and start_verse:
        reference = PassageReference(
            book=book,
            chapter=chapter,
            start_verse=start_verse,
            end_verse=end_verse,
        )
    return container.notes_service.list_notes(user_id, reference=reference)


@router.patch("/{note_id}")
def update_note(
    note_id: str,
    payload: UpdateNoteRequest,
    container: Container = Depends(get_container),
):
    try:
        return container.notes_service.update_note(
            note_id=note_id,
            body=payload.body,
            title=payload.title,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{note_id}")
def delete_note(note_id: str, container: Container = Depends(get_container)):
    container.notes_service.delete_note(note_id)
    return {"status": "deleted"}
