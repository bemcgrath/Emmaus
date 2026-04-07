from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from emmaus.domain.models import (
    ActionItem,
    EngagementSummary,
    MoodCheckIn,
    PrayerItem,
    SeenPassageRecord,
    SessionResponse,
    SpiritualMemoryEntry,
    SpiritualMemorySummary,
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

    def record_spiritual_memory(self, memory: SpiritualMemoryEntry) -> SpiritualMemoryEntry:
        self.get_or_create_profile(memory.user_id)
        return self.repository.add_spiritual_memory(memory)

    def list_spiritual_memories(self, user_id: str, limit: int = 5) -> list[SpiritualMemoryEntry]:
        return self.repository.list_spiritual_memories(user_id, limit=limit)

    def get_latest_spiritual_memory_for_session(self, session_id: str) -> SpiritualMemoryEntry | None:
        return self.repository.get_latest_spiritual_memory_for_session(session_id)

    def summarize_spiritual_memory(self, user_id: str, limit: int = 5) -> SpiritualMemorySummary:
        memories = self.list_spiritual_memories(user_id, limit=limit)
        if not memories:
            return SpiritualMemorySummary(user_id=user_id)

        latest = memories[0]
        recurring_themes = self._dedupe_preserve_order(
            theme
            for memory in memories
            for theme in memory.recurring_themes
        )
        growth_areas = self._dedupe_preserve_order(
            area
            for memory in memories
            for area in memory.growth_areas
        )
        recent_references = self._dedupe_preserve_order(
            self._format_reference(memory)
            for memory in memories
        )
        return SpiritualMemorySummary(
            user_id=user_id,
            latest_summary=latest.summary,
            recurring_themes=recurring_themes[:5],
            growth_areas=growth_areas[:5],
            carry_forward_prompt=latest.carry_forward_prompt,
            recent_references=recent_references[:5],
            memory_count=len(memories),
        )

    def record_passage_seen(self, user_id: str, focus_area: str, reference: dict) -> None:
        self.repository.record_passage_seen(user_id, focus_area, reference, datetime.now(UTC))

    def list_seen_passages(self, user_id: str, focus_area: str | None = None) -> list[SeenPassageRecord]:
        return self.repository.list_seen_passages(user_id, focus_area)

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
        self._refresh_spiritual_memory_from_action_follow_up(action_item)
        return action_item

    def create_prayer_item(self, prayer_item: PrayerItem) -> PrayerItem:
        self.get_or_create_profile(prayer_item.user_id)
        saved = self.repository.create_prayer_item(prayer_item)
        self.record_event(
            StudyEvent(
                user_id=prayer_item.user_id,
                event_type="prayer_item_created",
                notes=prayer_item.title,
            )
        )
        return saved

    def list_prayer_items(self, user_id: str, status: str | None = None) -> list[PrayerItem]:
        return self.repository.list_prayer_items(user_id, status)

    def mark_prayer_item_prayed(self, prayer_item_id: str, user_id: str) -> PrayerItem:
        prayer_item = self.repository.mark_prayer_item_prayed(prayer_item_id, datetime.now(UTC))
        if prayer_item is None or prayer_item.user_id != user_id:
            raise KeyError(f"Unknown prayer item '{prayer_item_id}'.")
        self.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="prayer_item_prayed",
                notes=prayer_item.title,
            )
        )
        return prayer_item

    def mark_prayer_item_answered(self, prayer_item_id: str, user_id: str) -> PrayerItem:
        prayer_item = self.repository.mark_prayer_item_answered(prayer_item_id, datetime.now(UTC))
        if prayer_item is None or prayer_item.user_id != user_id:
            raise KeyError(f"Unknown prayer item '{prayer_item_id}'.")
        self.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="prayer_item_answered",
                notes=prayer_item.title,
            )
        )
        return prayer_item

    def _refresh_spiritual_memory_from_action_follow_up(self, action_item: ActionItem) -> None:
        memory = self.get_latest_spiritual_memory_for_session(action_item.session_id)
        if memory is None:
            return

        updated_summary = self._update_memory_summary(memory.summary, action_item)
        updated_themes = self._update_memory_themes(memory.recurring_themes, action_item)
        updated_growth_areas = self._update_memory_growth_areas(memory.growth_areas, action_item)
        updated_prompt = self._update_carry_forward_prompt(memory.carry_forward_prompt, action_item)
        updated_memory = memory.model_copy(
            update={
                "summary": updated_summary,
                "recurring_themes": updated_themes,
                "growth_areas": updated_growth_areas,
                "carry_forward_prompt": updated_prompt,
            }
        )
        self.record_spiritual_memory(updated_memory)

    def _update_memory_summary(self, summary: str, action_item: ActionItem) -> str:
        note = (action_item.follow_up_note or "").strip()
        outcome = action_item.follow_up_outcome or "completed"
        if outcome == "completed":
            addition = f" The action step was completed: {note or action_item.title}."
        elif outcome == "prayed_through":
            addition = f" The user carried this forward through prayer: {note or action_item.title}."
        elif outcome == "discussed_with_someone":
            addition = f" The user processed this with someone else: {note or action_item.title}."
        else:
            addition = f" The user made partial progress and still has unfinished follow-through: {note or action_item.title}."
        return (summary.rstrip() + addition)[:320]

    def _update_memory_themes(self, themes: list[str], action_item: ActionItem) -> list[str]:
        updated = list(themes)
        outcome = action_item.follow_up_outcome or "completed"
        theme_map = {
            "completed": "completed follow-through",
            "partially_completed": "unfinished obedience that still needs revisiting",
            "prayed_through": "prayerful follow-through",
            "discussed_with_someone": "shared reflection with someone else",
        }
        updated.append(theme_map.get(outcome, "continued response"))
        return self._dedupe_preserve_order(updated)[:5]

    def _update_memory_growth_areas(self, growth_areas: list[str], action_item: ActionItem) -> list[str]:
        updated = [area for area in growth_areas if area != "turning insight into concrete follow-through"]
        outcome = action_item.follow_up_outcome or "completed"
        if outcome == "completed":
            updated.insert(0, "building on completed obedience")
        elif outcome == "partially_completed":
            updated.insert(0, "finishing what the passage has already surfaced")
        elif outcome == "prayed_through":
            updated.insert(0, "turning prayer into concrete obedience")
        elif outcome == "discussed_with_someone":
            updated.insert(0, "carrying reflection into honest conversation")
        return self._dedupe_preserve_order(updated)[:5]

    def _update_carry_forward_prompt(self, existing_prompt: str, action_item: ActionItem) -> str:
        outcome = action_item.follow_up_outcome or "completed"
        title = action_item.title
        if outcome == "completed":
            return f"Build on the completed step '{title}' and ask what fresh obedience Christ is inviting next."[:180]
        if outcome == "partially_completed":
            return f"Return to '{title}' and finish the part that still feels resisted or unfinished."[:180]
        if outcome == "prayed_through":
            return f"Keep praying through '{title}', then move toward one concrete act that matches those prayers."[:180]
        if outcome == "discussed_with_someone":
            return f"Revisit what surfaced in '{title}' and decide what personal follow-through should come after that conversation."[:180]
        return existing_prompt[:180]

    def get_engagement_summary(self, user_id: str) -> EngagementSummary:
        profile = self.get_profile(user_id)
        return EngagementSummary(
            user_id=user_id,
            completed_sessions=profile.completed_sessions,
            current_streak=profile.current_streak,
            longest_streak=profile.longest_streak,
            last_completed_on=profile.last_completed_on,
        )

    def _dedupe_preserve_order(self, values: Any) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            normalized = str(value).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered

    def _format_reference(self, memory: SpiritualMemoryEntry) -> str:
        reference = memory.reference
        if reference.end_verse and reference.end_verse != reference.start_verse:
            return f"{reference.book} {reference.chapter}:{reference.start_verse}-{reference.end_verse}"
        return f"{reference.book} {reference.chapter}:{reference.start_verse}"
