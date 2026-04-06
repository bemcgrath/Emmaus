from __future__ import annotations

from datetime import UTC, date, datetime
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


class UserPreferences(BaseModel):
    preferred_translation_source_id: str | None = None
    preferred_difficulty: Literal["gentle", "balanced", "challenging"] = "balanced"
    preferred_session_minutes: int = 20
    preferred_guide_mode: Literal["guide", "peer", "challenger", "coach"] = "guide"
    preferred_question_style: Literal["concise", "reflective", "probing", "practical"] = "reflective"
    preferred_guidance_tone: Literal["warm", "steady", "direct"] = "steady"
    nudge_intensity: Literal["gentle", "balanced", "direct"] = "balanced"
    preferred_study_days: list[str] = Field(default_factory=list)
    timezone: str = "UTC"
    preferred_study_window_start: str | None = None
    preferred_study_window_end: str | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


class UserProfile(BaseModel):
    user_id: str
    display_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_seen_at: datetime | None = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    completed_sessions: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_completed_on: date | None = None


class StudyEvent(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: Literal[
        "session_started",
        "question_answered",
        "reflection_saved",
        "passage_viewed",
        "session_completed",
        "action_item_completed",
        "mood_logged",
        "prayer_item_created",
        "prayer_item_prayed",
        "prayer_item_answered",
    ]
    reference: PassageReference | None = None
    difficulty: Literal["gentle", "balanced", "challenging"] = "balanced"
    engagement_score: int = 3
    notes: str | None = None


class MoodCheckIn(BaseModel):
    user_id: str
    mood: Literal["encouraged", "peaceful", "neutral", "anxious", "stressed", "discouraged"]
    energy: Literal["low", "medium", "high"] = "medium"
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StudyPatternSummary(BaseModel):
    user_id: str
    average_engagement: float
    preferred_difficulty: Literal["gentle", "balanced", "challenging"]
    recent_topics: list[str] = Field(default_factory=list)
    recommended_session_minutes: int


class StudyStyleProfile(BaseModel):
    user_id: str
    question_style: Literal["concise", "reflective", "probing", "practical"]
    guidance_tone: Literal["warm", "steady", "direct"]
    reason: str


class StudyQuestion(BaseModel):
    question: str
    type: Literal["observation", "interpretation", "application", "reflection"]
    difficulty: Literal["gentle", "balanced", "challenging"]


class StudyPlanStep(BaseModel):
    title: str
    instruction: str
    estimated_minutes: int


class ActionItem(BaseModel):
    action_item_id: str
    user_id: str
    session_id: str
    title: str
    detail: str
    status: Literal["open", "completed"] = "open"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    follow_up_note: str | None = None
    follow_up_outcome: Literal["completed", "partially_completed", "prayed_through", "discussed_with_someone"] | None = None


class PrayerItem(BaseModel):
    prayer_item_id: str
    user_id: str
    title: str
    detail: str
    status: Literal["active", "answered"] = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_prayed_at: datetime | None = None
    answered_at: datetime | None = None
    related_session_id: str | None = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    question_index: int
    question: str
    question_type: Literal["observation", "interpretation", "application", "reflection"]
    response_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StudyResponseEvaluation(BaseModel):
    question_type: Literal["observation", "interpretation", "application", "reflection"]
    comprehension_score: float = Field(ge=0, le=1)
    application_score: float = Field(ge=0, le=1)
    clarity_score: float = Field(ge=0, le=1)
    recommended_focus: Literal["comprehension", "application", "consistency", "growth"] = "growth"
    encouragement: str
    observed_patterns: list[str] = Field(default_factory=list)


class SpiritualMemoryEntry(BaseModel):
    memory_id: str
    user_id: str
    session_id: str
    reference: PassageReference
    summary: str
    recurring_themes: list[str] = Field(default_factory=list)
    growth_areas: list[str] = Field(default_factory=list)
    carry_forward_prompt: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SpiritualMemorySummary(BaseModel):
    user_id: str
    latest_summary: str | None = None
    recurring_themes: list[str] = Field(default_factory=list)
    growth_areas: list[str] = Field(default_factory=list)
    carry_forward_prompt: str | None = None
    recent_references: list[str] = Field(default_factory=list)
    memory_count: int = 0


class StudySession(BaseModel):
    session_id: str
    user_id: str
    status: Literal["active", "completed"] = "active"
    entry_point: str = "continue"
    guide_mode: Literal["guide", "peer", "challenger", "coach"] = "guide"
    requested_minutes: int = 20
    text_source_id: str
    commentary_source_id: str | None = None
    llm_source_id: str = "local_rules"
    reference: PassageReference
    questions: list[StudyQuestion]
    plan: list[StudyPlanStep]
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    current_question_index: int = 0
    latest_message: str
    action_item_id: str | None = None


class EngagementSummary(BaseModel):
    user_id: str
    completed_sessions: int
    current_streak: int
    longest_streak: int
    last_completed_on: date | None = None


class StudyGapReport(BaseModel):
    user_id: str
    comprehension_gap: float = Field(ge=0, le=1)
    application_gap: float = Field(ge=0, le=1)
    consistency_gap: float = Field(ge=0, le=1)
    focus_area: Literal["comprehension", "application", "consistency", "growth"]
    observed_patterns: list[str] = Field(default_factory=list)


class StudyRecommendation(BaseModel):
    user_id: str
    focus_area: Literal["comprehension", "application", "consistency", "growth"]
    recommended_reference: PassageReference
    recommended_guide_mode: Literal["guide", "peer", "challenger", "coach"]
    recommended_minutes: int
    recommended_entry_point: str
    reason: str
    suggested_action: str
    gap_report: StudyGapReport


class NudgePreview(BaseModel):
    user_id: str
    nudge_type: Literal["momentum", "restart", "follow_through", "encouragement", "theme"]
    title: str
    message: str
    recommended_entry_point: str
    recommended_minutes: int
    recommended_guide_mode: Literal["guide", "peer", "challenger", "coach"]
    recommendation: StudyRecommendation
    timing_decision: Literal["now", "later_today", "not_today"]
    timing_reason: str
    scheduled_for: datetime | None = None
    local_timezone: str


class NudgeDeliveryPlan(BaseModel):
    user_id: str
    delivery_status: Literal["send_now", "scheduled", "suppressed"]
    delivery_channel: Literal["push", "in_app"] = "push"
    deliver_at: datetime | None = None
    fallback_at: datetime | None = None
    idempotency_key: str
    reason: str
    nudge: NudgePreview


class AgentStudyResponse(BaseModel):
    message: str
    questions: list[StudyQuestion]
    plan: list[StudyPlanStep]
    pattern_summary: StudyPatternSummary


class AgentSessionStartResponse(BaseModel):
    session: StudySession
    passage: PassageText
    commentary: list[CommentaryNote]
    pattern_summary: StudyPatternSummary
    recommendation: StudyRecommendation
    current_question: StudyQuestion | None = None


class AgentSessionTurnResponse(BaseModel):
    session: StudySession
    reply_message: str
    next_question: StudyQuestion | None = None
    remaining_questions: int
    evaluation: StudyResponseEvaluation


class AgentSessionCompleteResponse(BaseModel):
    session: StudySession
    action_item: ActionItem
    engagement: EngagementSummary
