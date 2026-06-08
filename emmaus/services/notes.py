from __future__ import annotations

import uuid
from datetime import UTC, datetime

from emmaus.domain.models import PassageReference, StudyNote
from emmaus.repositories.study import SQLiteStudyRepository


class NotesService:
    def __init__(self, repository: SQLiteStudyRepository) -> None:
        self._repository = repository

    def create_note(
        self,
        user_id: str,
        reference: PassageReference,
        body: str,
        title: str | None = None,
        session_id: str | None = None,
    ) -> StudyNote:
        if not body.strip():
            raise ValueError("Note body cannot be empty.")
        now = datetime.now(UTC)
        note = StudyNote(
            note_id=str(uuid.uuid4()),
            user_id=user_id,
            reference=reference,
            title=title.strip() if title else None,
            body=body.strip(),
            session_id=session_id,
            created_at=now,
            updated_at=now,
        )
        return self._repository.save_study_note(note)

    def update_note(
        self,
        note_id: str,
        body: str | None = None,
        title: str | None = None,
    ) -> StudyNote:
        existing = self._repository.get_study_note(note_id)
        if existing is None:
            raise LookupError(f"Note '{note_id}' not found.")
        updates: dict[str, object] = {"updated_at": datetime.now(UTC)}
        if body is not None:
            if not body.strip():
                raise ValueError("Note body cannot be empty.")
            updates["body"] = body.strip()
        if title is not None:
            updates["title"] = title.strip() or None
        updated = existing.model_copy(update=updates)
        return self._repository.save_study_note(updated)

    def delete_note(self, note_id: str) -> None:
        self._repository.delete_study_note(note_id)

    def list_notes(self, user_id: str, reference: PassageReference | None = None) -> list[StudyNote]:
        return self._repository.list_study_notes(user_id, reference=reference)
