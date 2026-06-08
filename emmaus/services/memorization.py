from __future__ import annotations

import re
import uuid
from datetime import UTC, date, datetime, timedelta
from itertools import zip_longest

from emmaus.domain.models import (
    DrillAttemptResult,
    MasteryBreakdown,
    MemorizationProgress,
    MemorizationReview,
    MemorizationTarget,
    MemorizedVerse,
    PassageReference,
    WordDiff,
)
from emmaus.providers.text import TextProviderRegistry
from emmaus.repositories.study import SQLiteStudyRepository

MIN_EASE = 1.3
MAX_EASE = 2.8
ESV_SOURCE_ID = "esv"
DRILL_ADVANCE_THRESHOLD = 0.90
FINAL_LEARNING_STAGE = 4
MASTERED_INITIAL_INTERVAL_DAYS = 2
_WORD_TOKEN_RE = re.compile(r"[a-z0-9']+")


class MemorizationService:
    def __init__(self, repository: SQLiteStudyRepository, text_registry: TextProviderRegistry) -> None:
        self._repository = repository
        self._text_registry = text_registry

    def add_verse(self, user_id: str, reference: PassageReference) -> MemorizedVerse:
        try:
            provider = self._text_registry.get(ESV_SOURCE_ID)
        except KeyError as exc:
            raise LookupError(
                "ESV is not configured. Connect ESV in Profile before adding verses to memorization."
            ) from exc

        passage = provider.get_passage(reference)
        verse = MemorizedVerse(
            verse_id=str(uuid.uuid4()),
            user_id=user_id,
            reference=reference,
            verse_text=passage.text,
            translation=passage.translation_name,
            next_review_at=datetime.now(UTC).date(),
        )
        return self._repository.save_memorized_verse(verse)

    def list_verses(self, user_id: str) -> list[MemorizedVerse]:
        return self._repository.list_memorized_verses(user_id)

    def list_due_today(self, user_id: str) -> list[MemorizedVerse]:
        return self._repository.list_due_memorized_verses(user_id, datetime.now(UTC).date())

    def delete_verse(self, verse_id: str) -> None:
        self._repository.delete_memorized_verse(verse_id)

    def submit_drill_attempt(self, verse_id: str, typed_text: str) -> DrillAttemptResult:
        verse = self._repository.get_memorized_verse(verse_id)
        if verse is None:
            raise LookupError(f"Memorized verse '{verse_id}' not found.")
        if verse.mastery_level == "mastered":
            raise PermissionError(
                "Verse is already mastered. Use the review flow instead of drill attempts."
            )

        expected_tokens = _tokenize(verse.verse_text)
        typed_tokens = _tokenize(typed_text)
        diff = [
            WordDiff(expected=expected or "", typed=typed or "", ok=(expected == typed and expected is not None))
            for expected, typed in zip_longest(expected_tokens, typed_tokens, fillvalue=None)
        ]
        total_words = len(expected_tokens)
        correct_words = sum(1 for entry in diff if entry.ok)
        score = (correct_words / total_words) if total_words > 0 else 0.0

        now = datetime.now(UTC)
        advanced = False
        mastered_now = False
        updates: dict[str, object] = {"last_reviewed_at": now}

        if score >= DRILL_ADVANCE_THRESHOLD:
            if verse.learning_stage < FINAL_LEARNING_STAGE:
                updates["learning_stage"] = verse.learning_stage + 1
                advanced = True
            else:
                mastered_now = True
                updates.update(
                    {
                        "learning_stage": FINAL_LEARNING_STAGE,
                        "mastery_level": "mastered",
                        "ease_factor": 2.5,
                        "interval_days": MASTERED_INITIAL_INTERVAL_DAYS,
                        "repetition_count": 1,
                        "next_review_at": (now + timedelta(days=MASTERED_INITIAL_INTERVAL_DAYS)).date(),
                    }
                )

        updated = verse.model_copy(update=updates)
        self._repository.save_memorized_verse(updated)

        if mastered_now:
            self._repository.add_memorization_review(
                MemorizationReview(
                    review_id=str(uuid.uuid4()),
                    verse_id=verse_id,
                    user_id=verse.user_id,
                    rating="good",
                    drill_stage=FINAL_LEARNING_STAGE,
                    reviewed_at=now,
                )
            )

        return DrillAttemptResult(
            verse=updated,
            score=round(score, 4),
            correct_words=correct_words,
            total_words=total_words,
            advanced=advanced,
            mastered=mastered_now,
            diff=diff,
        )

    def apply_review(self, verse_id: str, rating: str, drill_stage: int) -> MemorizedVerse:
        verse = self._repository.get_memorized_verse(verse_id)
        if verse is None:
            raise LookupError(f"Memorized verse '{verse_id}' not found.")

        ease = verse.ease_factor
        interval = verse.interval_days
        reps = verse.repetition_count

        if rating == "again":
            reps = 0
            interval = 0
            ease = max(MIN_EASE, ease - 0.20)
        elif rating == "hard":
            reps += 1
            interval = max(1, int(round(max(interval, 1) * 1.2)))
            ease = max(MIN_EASE, ease - 0.15)
        elif rating == "good":
            reps += 1
            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 3
            else:
                interval = max(1, int(round(max(interval, 1) * ease)))
        elif rating == "easy":
            reps += 1
            if reps == 1:
                interval = 2
            elif reps == 2:
                interval = 5
            else:
                interval = max(2, int(round(max(interval, 1) * ease * 1.3)))
            ease = min(MAX_EASE, ease + 0.15)
        else:
            raise ValueError(f"Unknown rating '{rating}'.")

        now = datetime.now(UTC)
        next_review = (now + timedelta(days=interval)).date() if interval > 0 else now.date()
        mastery = _classify_mastery(reps, ease)

        updated = verse.model_copy(
            update={
                "ease_factor": round(ease, 3),
                "interval_days": interval,
                "repetition_count": reps,
                "next_review_at": next_review,
                "mastery_level": mastery,
                "last_reviewed_at": now,
            }
        )
        self._repository.save_memorized_verse(updated)
        self._repository.add_memorization_review(
            MemorizationReview(
                review_id=str(uuid.uuid4()),
                verse_id=verse_id,
                user_id=verse.user_id,
                rating=rating,  # type: ignore[arg-type]
                drill_stage=drill_stage,
                reviewed_at=now,
            )
        )
        return updated

    def set_target(
        self,
        user_id: str,
        title: str,
        verse_count_goal: int,
        target_date: date,
    ) -> MemorizationTarget:
        existing = self._repository.get_active_memorization_target(user_id)
        if existing is not None:
            updated = existing.model_copy(update={"status": "abandoned"})
            self._repository.save_memorization_target(updated)

        target = MemorizationTarget(
            target_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            verse_count_goal=verse_count_goal,
            target_date=target_date,
        )
        return self._repository.save_memorization_target(target)

    def list_targets(self, user_id: str) -> list[MemorizationTarget]:
        return self._repository.list_memorization_targets(user_id)

    def build_progress(self, user_id: str) -> MemorizationProgress:
        verses = self._repository.list_memorized_verses(user_id)
        breakdown = MasteryBreakdown()
        for verse in verses:
            if verse.mastery_level == "learning":
                breakdown.learning += 1
            elif verse.mastery_level == "familiar":
                breakdown.familiar += 1
            elif verse.mastery_level == "mastered":
                breakdown.mastered += 1

        review_dates = self._repository.list_memorization_review_dates(user_id)
        current_streak, longest_streak = _compute_streaks(review_dates)
        due_today = len(self.list_due_today(user_id))

        active_target = self._repository.get_active_memorization_target(user_id)
        active_progress = 0
        if active_target is not None:
            active_progress = sum(
                1
                for verse in verses
                if verse.added_at >= active_target.created_at
                and verse.mastery_level in ("familiar", "mastered")
            )
            if active_progress >= active_target.verse_count_goal and active_target.status == "active":
                active_target = active_target.model_copy(update={"status": "achieved"})
                self._repository.save_memorization_target(active_target)

        return MemorizationProgress(
            user_id=user_id,
            total_verses=len(verses),
            mastery=breakdown,
            current_streak=current_streak,
            longest_streak=longest_streak,
            due_today=due_today,
            active_target=active_target,
            active_target_progress=active_progress,
        )


def _tokenize(text: str) -> list[str]:
    return _WORD_TOKEN_RE.findall(text.lower())


def _classify_mastery(reps: int, ease: float) -> str:
    if reps >= 5 and ease >= 2.5:
        return "mastered"
    if reps >= 2 and ease >= 2.3:
        return "familiar"
    return "learning"


def _compute_streaks(review_dates: list[date]) -> tuple[int, int]:
    if not review_dates:
        return 0, 0
    unique_dates = sorted(set(review_dates), reverse=True)
    longest = 1
    run = 1
    for previous, current in zip(unique_dates, unique_dates[1:]):
        if (previous - current).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    today = datetime.now(UTC).date()
    if unique_dates[0] not in {today, today - timedelta(days=1)}:
        return 0, longest
    current_streak = 1
    for previous, current in zip(unique_dates, unique_dates[1:]):
        if (previous - current).days == 1:
            current_streak += 1
        else:
            break
    return current_streak, longest
