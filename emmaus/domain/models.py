from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class PassageReference(BaseModel):
    book: str
    chapter: int
    start_verse: int
    end_verse: int | None = None


class PassageText(BaseModel):
    source_id: str
    translation_name: str
    reference: PassageReference
    text: str
    copyright_notice: str | None = None


class TextSourceDescriptor(BaseModel):
    source_id: str
    name: str
    provider_type: Literal["local_file", "remote_api"]
    license_name: str
    supports_api_key: bool = False
    supports_local_file: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommentaryNote(BaseModel):
    source_id: str
    title: str
    body: str
    reference: PassageReference
    metadata: dict[str, Any] = Field(default_factory=dict)


class StudyEvent(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: Literal["session_started", "question_answered", "reflection_saved", "passage_viewed"]
    reference: PassageReference | None = None
    difficulty: Literal["gentle", "balanced", "challenging"] = "balanced"
    engagement_score: int = 3
    notes: str | None = None


class StudyPatternSummary(BaseModel):
    user_id: str
    average_engagement: float
    preferred_difficulty: Literal["gentle", "balanced", "challenging"]
    recent_topics: list[str] = Field(default_factory=list)
    recommended_session_minutes: int


class StudyQuestion(BaseModel):
    question: str
    type: Literal["observation", "interpretation", "application", "reflection"]
    difficulty: Literal["gentle", "balanced", "challenging"]


class StudyPlanStep(BaseModel):
    title: str
    instruction: str
    estimated_minutes: int


class AgentStudyResponse(BaseModel):
    message: str
    questions: list[StudyQuestion]
    plan: list[StudyPlanStep]
    pattern_summary: StudyPatternSummary
