from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from emmaus.domain.models import (
    ActionItem,
    EngagementSummary,
    MoodCheckIn,
    SessionResponse,
    StudyEvent,
    StudyPatternSummary,
    StudySession,
    UserProfile,
)
from emmaus.repositories.study import SQLiteStudyRepository


class StudyService:
    def __init__(self, repository: SQLiteStudyRepository, history_limit: int) -> None:
        self.repository = repository
        self.history_limit = history_limit

    def get_or_create_profile(self, user_id: str, display_name: str | None = None) -> UserProfile:
        return self.repository.get_or_create_user(user_id, display_name)

    def get_profile(self, user_id: str) -> UserProfile:
        profile = self.repository.get_user_profile(user_id)
        if profile is None:
            profile = self.repository.get_or_create_user(user_id)
        return profile

    def update_preferences(
        self,
        user_id: str,
        updates: dict[str, Any],
        display_name: str | None = None,
    ) -> UserProfile:
        profile = self.get_or_create_profile(user_id, display_name)
        preference_updates = {key: value for key, value in updates.items() if value is not None}
        updated = profile.model_copy(
            update={
                "display_name": display_name or profile.display_name,
                "last_seen_at": datetime.now(UTC),
                "preferences": profile.preferences.model_copy(update=preference_updates),
            }
        )
        return self.repository.save_user_profile(updated)

    def record_event(self, event: StudyEvent) -> StudyEvent:
        self.get_or_create_profile(event.user_id)
        return self.repository.add_event(event)

    def list_events(self, user_id: str) -> list[StudyEvent]:
        events = self.repository.list_events(user_id)
        return events[-self.history_limit :]

    def record_mood_checkin(self, mood_checkin: MoodCheckIn) -> MoodCheckIn:
        self.get_or_create_profile(mood_checkin.user_id)
        saved = self.repository.add_mood_checkin(mood_checkin)
        self.record_event(
            StudyEvent(
                user_id=mood_checkin.user_id,
                event_type="mood_logged",
                engagement_score=3,
                notes=f"{mood_checkin.mood}:{mood_checkin.energy}",
            )
        )
        return saved

    def get_latest_mood_checkin(self, user_id: str) -> MoodCheckIn | None:
        return self.repository.get_latest_mood_checkin(user_id)

    def summarize_patterns(self, user_id: str) -> StudyPatternSummary:
        profile = self.get_profile(user_id)
        events = self.list_events(user_id)
        if not events:
            return StudyPatternSummary(
                user_id=user_id,
                average_engagement=3.0,
                preferred_difficulty=profile.preferences.preferred_difficulty,
                recent_topics=[],
                recommended_session_minutes=profile.preferences.preferred_session_minutes,
            )

        average_engagement = round(sum(event.engagement_score for event in events) / len(events), 2)
        preferred_difficulty = Counter(event.difficulty for event in events if event.event_type != "mood_logged").most_common(1)
        difficulty = preferred_difficulty[0][0] if preferred_difficulty else profile.preferences.preferred_difficulty
        topics = [
            f"{event.reference.book} {event.reference.chapter}"
            for event in events
            if event.reference is not None
        ]

        recommended_minutes = profile.preferences.preferred_session_minutes
        if average_engagement < 2.5:
            recommended_minutes = max(10, recommended_minutes - 5)
        elif average_engagement >= 4:
            recommended_minutes = min(40, recommended_minutes + 5)

        latest_mood = self.get_latest_mood_checkin(user_id)
        if latest_mood is not None:
            if latest_mood.energy == "low":
                recommended_minutes = max(5, recommended_minutes - 5)
            elif latest_mood.energy == "high":
                recommended_minutes = min(40, recommended_minutes + 5)

        return StudyPatternSummary(
            user_id=user_id,
            average_engagement=average_engagement,
            preferred_difficulty=difficulty,
            recent_topics=topics[-5:],
            recommended_session_minutes=recommended_minutes,
        )

    def create_session(self, session: StudySession) -> StudySession:
        self.get_or_create_profile(session.user_id)
        return self.repository.create_session(session)

    def get_session(self, session_id: str) -> StudySession:
        session = self.repository.get_session(session_id)
        if session is None:
            raise KeyError(f"Unknown session '{session_id}'.")
        return session

    def get_active_session(self, user_id: str) -> StudySession | None:
        sessions = self.repository.list_sessions(user_id, status="active")
        return sessions[0] if sessions else None

    def list_sessions(self, user_id: str, status: str | None = None) -> list[StudySession]:
        return self.repository.list_sessions(user_id, status)

    def save_session(self, session: StudySession) -> StudySession:
        return self.repository.save_session(session)

    def add_session_response(self, response: SessionResponse) -> SessionResponse:
        return self.repository.add_session_response(response)

    def list_session_responses(self, session_id: str) -> list[SessionResponse]:
        return self.repository.list_session_responses(session_id)

    def list_recent_responses(self, user_id: str, limit_sessions: int = 5) -> list[SessionResponse]:
        sessions = self.list_sessions(user_id, status="completed")[:limit_sessions]
        responses: list[SessionResponse] = []
        for session in sessions:
            responses.extend(self.list_session_responses(session.session_id))
        return responses

    def create_action_item(self, action_item: ActionItem) -> ActionItem:
        return self.repository.create_action_item(action_item)

    def list_action_items(self, user_id: str, status: str | None = None) -> list[ActionItem]:
        return self.repository.list_action_items(user_id, status)

    def complete_action_item(
        self,
        action_item_id: str,
        user_id: str,
        follow_up_note: str | None = None,
        follow_up_outcome: str | None = None,
    ) -> ActionItem:
        action_item = self.repository.complete_action_item(
            action_item_id,
            datetime.now(UTC),
            follow_up_note=follow_up_note,
            follow_up_outcome=follow_up_outcome,
        )
        if action_item is None or action_item.user_id != user_id:
            raise KeyError(f"Unknown action item '{action_item_id}'.")
        summary_bits = [action_item.title]
        if follow_up_outcome:
            summary_bits.append(f"outcome={follow_up_outcome}")
        if follow_up_note:
            summary_bits.append(follow_up_note[:180])
        self.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="action_item_completed",
                notes=" | ".join(summary_bits),
            )
        )
        return action_item

    def get_engagement_summary(self, user_id: str) -> EngagementSummary:
        profile = self.get_profile(user_id)
        return EngagementSummary(
            user_id=user_id,
            completed_sessions=profile.completed_sessions,
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            last_completed_on=profile.last_completed_on,
        )
