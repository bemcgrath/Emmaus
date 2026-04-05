from __future__ import annotations

from collections import Counter

from emmaus.domain.models import StudyEvent, StudyPatternSummary
from emmaus.repositories.study import InMemoryStudyRepository


class StudyService:
    def __init__(self, repository: InMemoryStudyRepository, history_limit: int) -> None:
        self.repository = repository
        self.history_limit = history_limit

    def record_event(self, event: StudyEvent) -> StudyEvent:
        return self.repository.add_event(event)

    def list_events(self, user_id: str) -> list[StudyEvent]:
        events = self.repository.list_events(user_id)
        return events[-self.history_limit :]

    def summarize_patterns(self, user_id: str) -> StudyPatternSummary:
        events = self.list_events(user_id)
        if not events:
            return StudyPatternSummary(
                user_id=user_id,
                average_engagement=3.0,
                preferred_difficulty="balanced",
                recent_topics=[],
                recommended_session_minutes=20,
            )

        average_engagement = round(sum(event.engagement_score for event in events) / len(events), 2)
        preferred_difficulty = Counter(event.difficulty for event in events).most_common(1)[0][0]
        topics = [
            f"{event.reference.book} {event.reference.chapter}"
            for event in events
            if event.reference is not None
        ]

        recommended_minutes = 15 if average_engagement < 2.5 else 20 if average_engagement < 4 else 30
        return StudyPatternSummary(
            user_id=user_id,
            average_engagement=average_engagement,
            preferred_difficulty=preferred_difficulty,
            recent_topics=topics[-5:],
            recommended_session_minutes=recommended_minutes,
        )
