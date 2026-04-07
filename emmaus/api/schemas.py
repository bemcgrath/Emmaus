from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from emmaus.domain.models import MoodCheckIn, PassageReference, StudyEvent


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


class RegisterESVTextSourceRequest(BaseModel):
    api_key: str = Field(min_length=1)
    source_id: str = Field(default="esv", pattern=r"^[a-z0-9_\-]+$")
    name: str = "ESV"
    license_name: str = "Crossway API Terms"


class RegisterUploadedTextSourceRequest(BaseModel):
    source_id: str = Field(pattern=r"^[a-z0-9_\-]+$")
    name: str
    filename: str
    file_content: str = Field(min_length=1)
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
    event_type: Literal[
        "session_started",
        "question_answered",
        "reflection_saved",
        "passage_viewed",
        "session_completed",
        "action_item_completed",
        "mood_logged",
    ]
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


class MoodCheckInRequest(BaseModel):
    user_id: str
    mood: Literal["encouraged", "peaceful", "neutral", "anxious", "stressed", "discouraged"]
    energy: Literal["low", "medium", "high"] = "medium"
    notes: str | None = None

    def to_model(self) -> MoodCheckIn:
        return MoodCheckIn(
            user_id=self.user_id,
            mood=self.mood,
            energy=self.energy,
            notes=self.notes,
        )


class AgentSessionRequest(BaseModel):
    user_id: str
    text_source_id: str | None = None
    commentary_source_id: str | None = None
    llm_source_id: str = "local_rules"
    reference: PassageReference


class StartAgentSessionRequest(BaseModel):
    user_id: str
    display_name: str | None = None
    text_source_id: str | None = None
    commentary_source_id: str | None = None
    llm_source_id: str = "local_rules"
    reference: PassageReference | None = None
    entry_point: str = "continue where I left off"
    requested_minutes: int | None = Field(default=None, ge=5, le=60)
    guide_mode: Literal["guide", "peer", "challenger", "coach"] | None = None


class RespondAgentSessionRequest(BaseModel):
    session_id: str
    user_id: str
    response_text: str = Field(min_length=1)
    engagement_score: int = Field(ge=1, le=5, default=3)


class UpdateActiveSessionRequest(BaseModel):
    session_id: str
    user_id: str
    requested_minutes: int = Field(ge=5, le=60)


class CompleteAgentSessionRequest(BaseModel):
    session_id: str
    user_id: str
    summary_notes: str | None = None
    action_item_title: str | None = None
    action_item_detail: str | None = None
    engagement_score: int = Field(ge=1, le=5, default=4)


class UpdateUserPreferencesRequest(BaseModel):
    display_name: str | None = None
    preferred_translation_source_id: str | None = None
    preferred_difficulty: Literal["gentle", "balanced", "challenging"] | None = None
    preferred_session_minutes: int | None = Field(default=None, ge=5, le=60)
    preferred_guide_mode: Literal["guide", "peer", "challenger", "coach"] | None = None
    preferred_question_style: Literal["concise", "reflective", "probing", "practical"] | None = None
    preferred_guidance_tone: Literal["warm", "steady", "direct"] | None = None
    nudge_intensity: Literal["gentle", "balanced", "direct"] | None = None
    preferred_study_days: list[str] | None = None
    timezone: str | None = None
    preferred_study_window_start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    preferred_study_window_end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    quiet_hours_start: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    quiet_hours_end: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")

    def preference_updates(self) -> dict[str, object]:
        return {
            "preferred_translation_source_id": self.preferred_translation_source_id,
            "preferred_difficulty": self.preferred_difficulty,
            "preferred_session_minutes": self.preferred_session_minutes,
            "preferred_guide_mode": self.preferred_guide_mode,
            "preferred_question_style": self.preferred_question_style,
            "preferred_guidance_tone": self.preferred_guidance_tone,
            "nudge_intensity": self.nudge_intensity,
            "preferred_study_days": self.preferred_study_days,
            "timezone": self.timezone,
            "preferred_study_window_start": self.preferred_study_window_start,
            "preferred_study_window_end": self.preferred_study_window_end,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
        }


class CreateActionItemRequest(BaseModel):
    user_id: str
    session_id: str
    title: str
    detail: str


class CompleteActionItemRequest(BaseModel):
    user_id: str
    follow_up_note: str | None = None
    follow_up_outcome: Literal["completed", "partially_completed", "prayed_through", "discussed_with_someone"] | None = None


class CreatePrayerItemRequest(BaseModel):
    user_id: str
    title: str
    detail: str
    related_session_id: str | None = None


class UpdatePrayerItemRequest(BaseModel):
    user_id: str


class NudgePreviewRequest(BaseModel):
    user_id: str
    preview_at: str | None = None

