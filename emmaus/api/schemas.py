from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from emmaus.domain.models import PassageReference, StudyEvent


class RegisterLocalTextSourceRequest(BaseModel):
    source_id: str = Field(pattern=r"^[a-z0-9_\-]+$")
    name: str
    file_path: str
    license_name: str = "User Supplied"


class RegisterApiTextSourceRequest(BaseModel):
    source_id: str = Field(pattern=r"^[a-z0-9_\-]+$")
    name: str
    base_url: HttpUrl
    api_key: str | None = None
    license_name: str = "User Supplied"


class PassageQuery(BaseModel):
    source_id: str | None = None
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


class StudyEventRequest(BaseModel):
    user_id: str
    event_type: Literal["session_started", "question_answered", "reflection_saved", "passage_viewed"]
    book: str | None = None
    chapter: int | None = None
    start_verse: int | None = None
    end_verse: int | None = None
    difficulty: Literal["gentle", "balanced", "challenging"] = "balanced"
    engagement_score: int = Field(ge=1, le=5, default=3)
    notes: str | None = None

    def to_model(self) -> StudyEvent:
        reference = None
        if self.book and self.chapter and self.start_verse:
            reference = PassageReference(
                book=self.book,
                chapter=self.chapter,
                start_verse=self.start_verse,
                end_verse=self.end_verse,
            )
        return StudyEvent(
            user_id=self.user_id,
            event_type=self.event_type,
            reference=reference,
            difficulty=self.difficulty,
            engagement_score=self.engagement_score,
            notes=self.notes,
        )


class AgentSessionRequest(BaseModel):
    user_id: str
    text_source_id: str | None = None
    commentary_source_id: str | None = None
    llm_source_id: str = "local_rules"
    reference: PassageReference
