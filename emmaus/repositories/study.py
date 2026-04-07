from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

from emmaus.domain.models import (
    ActionItem,
    MoodCheckIn,
    PrayerItem,
    SeenPassageRecord,
    SessionResponse,
    SpiritualMemoryEntry,
    StudyEvent,
    StudySession,
    UserPreferences,
    UserProfile,
)


class SQLiteStudyRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT,
                    preferences_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS study_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    reference_json TEXT,
                    difficulty TEXT NOT NULL,
                    engagement_score INTEGER NOT NULL,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS study_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    entry_point TEXT NOT NULL,
                    guide_mode TEXT NOT NULL,
                    requested_minutes INTEGER NOT NULL,
                    text_source_id TEXT NOT NULL,
                    commentary_source_id TEXT,
                    llm_source_id TEXT NOT NULL,
                    reference_json TEXT NOT NULL,
                    questions_json TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    current_question_index INTEGER NOT NULL,
                    latest_message TEXT NOT NULL,
                    action_item_id TEXT
                );

                CREATE TABLE IF NOT EXISTS session_responses (
                    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    question_index INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS action_items (
                    action_item_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    follow_up_note TEXT,
                    follow_up_outcome TEXT
                );

                CREATE TABLE IF NOT EXISTS mood_checkins (
                    mood_checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    energy TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS prayer_items (
                    prayer_item_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_prayed_at TEXT,
                    answered_at TEXT,
                    related_session_id TEXT
                );

                CREATE TABLE IF NOT EXISTS spiritual_memories (
                    memory_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    reference_json TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    recurring_themes_json TEXT NOT NULL,
                    growth_areas_json TEXT NOT NULL,
                    carry_forward_prompt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_passages_seen (
                    user_id TEXT NOT NULL,
                    focus_area TEXT NOT NULL,
                    reference_key TEXT NOT NULL,
                    reference_json TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    session_count INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, focus_area, reference_key)
                );
                """
            )
            self._ensure_column(connection, "action_items", "follow_up_note", "TEXT")
            self._ensure_column(connection, "action_items", "follow_up_outcome", "TEXT")

    def get_or_create_user(self, user_id: str, display_name: str | None = None) -> UserProfile:
        existing = self.get_user_profile(user_id)
        if existing is not None:
            if display_name and display_name != existing.display_name:
                updated = existing.model_copy(update={"display_name": display_name, "last_seen_at": datetime.now(UTC)})
                self.save_user_profile(updated)
                return updated
            return existing

        profile = UserProfile(
            user_id=user_id,
            display_name=display_name,
            last_seen_at=datetime.now(UTC),
        )
        self.save_user_profile(profile)
        return profile

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT user_id, display_name, created_at, last_seen_at, preferences_json FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            return None

        profile = UserProfile(
            user_id=row["user_id"],
            display_name=row["display_name"],
            created_at=self._parse_datetime(row["created_at"]),
            last_seen_at=self._parse_datetime(row["last_seen_at"]),
            preferences=UserPreferences.model_validate_json(row["preferences_json"]),
        )
        return self._enrich_profile(profile)

    def save_user_profile(self, profile: UserProfile) -> UserProfile:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (user_id, display_name, created_at, last_seen_at, preferences_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    created_at = excluded.created_at,
                    last_seen_at = excluded.last_seen_at,
                    preferences_json = excluded.preferences_json
                """,
                (
                    profile.user_id,
                    profile.display_name,
                    profile.created_at.isoformat(),
                    self._dt_or_none(profile.last_seen_at),
                    profile.preferences.model_dump_json(),
                ),
            )
        return self._enrich_profile(profile)

    def add_event(self, event: StudyEvent) -> StudyEvent:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO study_events (user_id, timestamp, event_type, reference_json, difficulty, engagement_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.user_id,
                    event.timestamp.isoformat(),
                    event.event_type,
                    json.dumps(event.reference.model_dump()) if event.reference else None,
                    event.difficulty,
                    event.engagement_score,
                    event.notes,
                ),
            )
        return event

    def list_events(self, user_id: str) -> list[StudyEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM study_events WHERE user_id = ? ORDER BY timestamp ASC",
                (user_id,),
            ).fetchall()
        events: list[StudyEvent] = []
        for row in rows:
            reference = json.loads(row["reference_json"]) if row["reference_json"] else None
            events.append(
                StudyEvent(
                    user_id=row["user_id"],
                    timestamp=self._parse_datetime(row["timestamp"]),
                    event_type=row["event_type"],
                    reference=reference,
                    difficulty=row["difficulty"],
                    engagement_score=row["engagement_score"],
                    notes=row["notes"],
                )
            )
        return events

    def add_mood_checkin(self, mood_checkin: MoodCheckIn) -> MoodCheckIn:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO mood_checkins (user_id, mood, energy, notes, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    mood_checkin.user_id,
                    mood_checkin.mood,
                    mood_checkin.energy,
                    mood_checkin.notes,
                    mood_checkin.created_at.isoformat(),
                ),
            )
        return mood_checkin

    def get_latest_mood_checkin(self, user_id: str) -> MoodCheckIn | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT user_id, mood, energy, notes, created_at FROM mood_checkins WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return MoodCheckIn(
            user_id=row["user_id"],
            mood=row["mood"],
            energy=row["energy"],
            notes=row["notes"],
            created_at=self._parse_datetime(row["created_at"]),
        )

    def create_session(self, session: StudySession) -> StudySession:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO study_sessions (
                    session_id, user_id, status, entry_point, guide_mode, requested_minutes, text_source_id,
                    commentary_source_id, llm_source_id, reference_json, questions_json, plan_json,
                    started_at, completed_at, current_question_index, latest_message, action_item_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.user_id,
                    session.status,
                    session.entry_point,
                    session.guide_mode,
                    session.requested_minutes,
                    session.text_source_id,
                    session.commentary_source_id,
                    session.llm_source_id,
                    json.dumps(session.reference.model_dump()),
                    json.dumps([question.model_dump() for question in session.questions]),
                    json.dumps([step.model_dump() for step in session.plan]),
                    session.started_at.isoformat(),
                    self._dt_or_none(session.completed_at),
                    session.current_question_index,
                    session.latest_message,
                    session.action_item_id,
                ),
            )
        return session

    def get_session(self, session_id: str) -> StudySession | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM study_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def list_sessions(self, user_id: str, status: str | None = None) -> list[StudySession]:
        query = "SELECT * FROM study_sessions WHERE user_id = ?"
        params: list[str] = [user_id]
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY started_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [self._row_to_session(row) for row in rows]

    def save_session(self, session: StudySession) -> StudySession:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE study_sessions
                SET status = ?, completed_at = ?, current_question_index = ?, latest_message = ?, action_item_id = ?
                WHERE session_id = ?
                """,
                (
                    session.status,
                    self._dt_or_none(session.completed_at),
                    session.current_question_index,
                    session.latest_message,
                    session.action_item_id,
                    session.session_id,
                ),
            )
        return session

    def add_session_response(self, response: SessionResponse) -> SessionResponse:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO session_responses (
                    session_id, user_id, question_index, question_text, question_type, response_text, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response.session_id,
                    response.user_id,
                    response.question_index,
                    response.question,
                    response.question_type,
                    response.response_text,
                    response.created_at.isoformat(),
                ),
            )
        return response

    def list_session_responses(self, session_id: str) -> list[SessionResponse]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM session_responses WHERE session_id = ? ORDER BY response_id ASC",
                (session_id,),
            ).fetchall()
        return [
            SessionResponse(
                session_id=row["session_id"],
                user_id=row["user_id"],
                question_index=row["question_index"],
                question=row["question_text"],
                question_type=row["question_type"],
                response_text=row["response_text"],
                created_at=self._parse_datetime(row["created_at"]),
            )
            for row in rows
        ]

    def create_action_item(self, action_item: ActionItem) -> ActionItem:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO action_items (
                    action_item_id, user_id, session_id, title, detail, status, created_at, completed_at, follow_up_note, follow_up_outcome
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action_item.action_item_id,
                    action_item.user_id,
                    action_item.session_id,
                    action_item.title,
                    action_item.detail,
                    action_item.status,
                    action_item.created_at.isoformat(),
                    self._dt_or_none(action_item.completed_at),
                    action_item.follow_up_note,
                    action_item.follow_up_outcome,
                ),
            )
        return action_item

    def get_action_item(self, action_item_id: str) -> ActionItem | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM action_items WHERE action_item_id = ?",
                (action_item_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_action_item(row)

    def list_action_items(self, user_id: str, status: str | None = None) -> list[ActionItem]:
        query = "SELECT * FROM action_items WHERE user_id = ?"
        params: list[str] = [user_id]
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [self._row_to_action_item(row) for row in rows]

    def complete_action_item(
        self,
        action_item_id: str,
        completed_at: datetime,
        follow_up_note: str | None = None,
        follow_up_outcome: str | None = None,
    ) -> ActionItem | None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE action_items
                SET status = 'completed', completed_at = ?, follow_up_note = ?, follow_up_outcome = ?
                WHERE action_item_id = ?
                """,
                (completed_at.isoformat(), follow_up_note, follow_up_outcome, action_item_id),
            )
        return self.get_action_item(action_item_id)

    def create_prayer_item(self, prayer_item: PrayerItem) -> PrayerItem:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO prayer_items (
                    prayer_item_id, user_id, title, detail, status, created_at, last_prayed_at, answered_at, related_session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prayer_item.prayer_item_id,
                    prayer_item.user_id,
                    prayer_item.title,
                    prayer_item.detail,
                    prayer_item.status,
                    prayer_item.created_at.isoformat(),
                    self._dt_or_none(prayer_item.last_prayed_at),
                    self._dt_or_none(prayer_item.answered_at),
                    prayer_item.related_session_id,
                ),
            )
        return prayer_item

    def get_prayer_item(self, prayer_item_id: str) -> PrayerItem | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM prayer_items WHERE prayer_item_id = ?",
                (prayer_item_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_prayer_item(row)

    def list_prayer_items(self, user_id: str, status: str | None = None) -> list[PrayerItem]:
        query = "SELECT * FROM prayer_items WHERE user_id = ?"
        params: list[str] = [user_id]
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [self._row_to_prayer_item(row) for row in rows]

    def mark_prayer_item_prayed(self, prayer_item_id: str, prayed_at: datetime) -> PrayerItem | None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE prayer_items
                SET last_prayed_at = ?
                WHERE prayer_item_id = ?
                """,
                (prayed_at.isoformat(), prayer_item_id),
            )
        return self.get_prayer_item(prayer_item_id)

    def mark_prayer_item_answered(self, prayer_item_id: str, answered_at: datetime) -> PrayerItem | None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE prayer_items
                SET status = 'answered', answered_at = ?
                WHERE prayer_item_id = ?
                """,
                (answered_at.isoformat(), prayer_item_id),
            )
        return self.get_prayer_item(prayer_item_id)

    def add_spiritual_memory(self, memory: SpiritualMemoryEntry) -> SpiritualMemoryEntry:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO spiritual_memories (
                    memory_id, user_id, session_id, reference_json, summary, recurring_themes_json,
                    growth_areas_json, carry_forward_prompt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    session_id = excluded.session_id,
                    reference_json = excluded.reference_json,
                    summary = excluded.summary,
                    recurring_themes_json = excluded.recurring_themes_json,
                    growth_areas_json = excluded.growth_areas_json,
                    carry_forward_prompt = excluded.carry_forward_prompt,
                    created_at = excluded.created_at
                """,
                (
                    memory.memory_id,
                    memory.user_id,
                    memory.session_id,
                    json.dumps(memory.reference.model_dump()),
                    memory.summary,
                    json.dumps(memory.recurring_themes),
                    json.dumps(memory.growth_areas),
                    memory.carry_forward_prompt,
                    memory.created_at.isoformat(),
                ),
            )
        return memory

    def get_latest_spiritual_memory_for_session(self, session_id: str) -> SpiritualMemoryEntry | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM spiritual_memories WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_memory(row)

    def list_spiritual_memories(self, user_id: str, limit: int | None = None) -> list[SpiritualMemoryEntry]:
        query = "SELECT * FROM spiritual_memories WHERE user_id = ? ORDER BY created_at DESC"
        params: list[object] = [user_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def record_passage_seen(
        self,
        user_id: str,
        focus_area: str,
        reference: dict,
        seen_at: datetime,
    ) -> None:
        reference_key = self._reference_key(reference)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_passages_seen (
                    user_id, focus_area, reference_key, reference_json, first_seen_at, last_seen_at, session_count
                ) VALUES (?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(user_id, focus_area, reference_key) DO UPDATE SET
                    reference_json = excluded.reference_json,
                    last_seen_at = excluded.last_seen_at,
                    session_count = user_passages_seen.session_count + 1
                """,
                (
                    user_id,
                    focus_area,
                    reference_key,
                    json.dumps(reference),
                    seen_at.isoformat(),
                    seen_at.isoformat(),
                ),
            )

    def list_seen_passages(self, user_id: str, focus_area: str | None = None) -> list[SeenPassageRecord]:
        query = "SELECT * FROM user_passages_seen WHERE user_id = ?"
        params: list[object] = [user_id]
        if focus_area is not None:
            query += " AND focus_area = ?"
            params.append(focus_area)
        query += " ORDER BY last_seen_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        return [self._row_to_seen_passage(row) for row in rows]

    def list_completed_session_dates(self, user_id: str) -> Sequence[date]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT completed_at FROM study_sessions WHERE user_id = ? AND status = 'completed' AND completed_at IS NOT NULL ORDER BY completed_at DESC",
                (user_id,),
            ).fetchall()
        return [self._parse_datetime(row["completed_at"]).date() for row in rows]

    def completed_sessions_count(self, user_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM study_sessions WHERE user_id = ? AND status = 'completed'",
                (user_id,),
            ).fetchone()
        return int(row["count"])

    def _enrich_profile(self, profile: UserProfile) -> UserProfile:
        completed_dates = list(self.list_completed_session_dates(profile.user_id))
        current_streak, longest_streak = self._compute_streaks(completed_dates)
        return profile.model_copy(
            update={
                "completed_sessions": self.completed_sessions_count(profile.user_id),
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "last_completed_on": completed_dates[0] if completed_dates else None,
            }
        )

    def _row_to_prayer_item(self, row: sqlite3.Row) -> PrayerItem:
        return PrayerItem(
            prayer_item_id=row["prayer_item_id"],
            user_id=row["user_id"],
            title=row["title"],
            detail=row["detail"],
            status=row["status"],
            created_at=self._parse_datetime(row["created_at"]),
            last_prayed_at=self._parse_datetime(row["last_prayed_at"]),
            answered_at=self._parse_datetime(row["answered_at"]),
            related_session_id=row["related_session_id"],
        )

    def _row_to_session(self, row: sqlite3.Row) -> StudySession:
        return StudySession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            status=row["status"],
            entry_point=row["entry_point"],
            guide_mode=row["guide_mode"],
            requested_minutes=row["requested_minutes"],
            text_source_id=row["text_source_id"],
            commentary_source_id=row["commentary_source_id"],
            llm_source_id=row["llm_source_id"],
            reference=json.loads(row["reference_json"]),
            questions=json.loads(row["questions_json"]),
            plan=json.loads(row["plan_json"]),
            started_at=self._parse_datetime(row["started_at"]),
            completed_at=self._parse_datetime(row["completed_at"]),
            current_question_index=row["current_question_index"],
            latest_message=row["latest_message"],
            action_item_id=row["action_item_id"],
        )

    def _row_to_action_item(self, row: sqlite3.Row) -> ActionItem:
        return ActionItem(
            action_item_id=row["action_item_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            title=row["title"],
            detail=row["detail"],
            status=row["status"],
            created_at=self._parse_datetime(row["created_at"]),
            completed_at=self._parse_datetime(row["completed_at"]),
            follow_up_note=row["follow_up_note"] if "follow_up_note" in row.keys() else None,
            follow_up_outcome=row["follow_up_outcome"] if "follow_up_outcome" in row.keys() else None,
        )

    def _row_to_memory(self, row: sqlite3.Row) -> SpiritualMemoryEntry:
        return SpiritualMemoryEntry(
            memory_id=row["memory_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            reference=json.loads(row["reference_json"]),
            summary=row["summary"],
            recurring_themes=json.loads(row["recurring_themes_json"]),
            growth_areas=json.loads(row["growth_areas_json"]),
            carry_forward_prompt=row["carry_forward_prompt"],
            created_at=self._parse_datetime(row["created_at"]),
        )

    def _row_to_seen_passage(self, row: sqlite3.Row) -> SeenPassageRecord:
        return SeenPassageRecord(
            user_id=row["user_id"],
            focus_area=row["focus_area"],
            reference=json.loads(row["reference_json"]),
            first_seen_at=self._parse_datetime(row["first_seen_at"]),
            last_seen_at=self._parse_datetime(row["last_seen_at"]),
            session_count=row["session_count"],
        )

    def _compute_streaks(self, completed_dates: Sequence[date]) -> tuple[int, int]:
        if not completed_dates:
            return 0, 0
        unique_dates = sorted(set(completed_dates), reverse=True)
        longest = 1
        current_run = 1
        for previous, current in zip(unique_dates, unique_dates[1:]):
            if (previous - current).days == 1:
                current_run += 1
                longest = max(longest, current_run)
            else:
                current_run = 1
        current_streak = 1
        today = datetime.now(UTC).date()
        if unique_dates[0] not in {today, date.fromordinal(today.toordinal() - 1)}:
            current_streak = 0
        else:
            current_streak = 1
            for previous, current in zip(unique_dates, unique_dates[1:]):
                if (previous - current).days == 1:
                    current_streak += 1
                else:
                    break
        return current_streak, longest

    def _ensure_column(self, connection: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing_columns = {row[1] for row in rows}
        if column_name not in existing_columns:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _reference_key(self, reference: dict) -> str:
        end_verse = reference.get("end_verse")
        return f"{reference['book']}|{reference['chapter']}|{reference['start_verse']}|{end_verse or reference['start_verse']}"

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    def _dt_or_none(self, value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None
