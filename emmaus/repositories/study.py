from __future__ import annotations

from collections import defaultdict

from emmaus.domain.models import StudyEvent


class InMemoryStudyRepository:
    def __init__(self) -> None:
        self._events: dict[str, list[StudyEvent]] = defaultdict(list)

    def add_event(self, event: StudyEvent) -> StudyEvent:
        self._events[event.user_id].append(event)
        return event

    def list_events(self, user_id: str) -> list[StudyEvent]:
        return list(self._events[user_id])
