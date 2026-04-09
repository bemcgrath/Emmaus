from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from emmaus.domain.models import (
    NudgeDeliveryPlan,
    NudgePreview,
    PassageReference,
    SessionResponse,
    StudyGapReport,
    StudyRecommendation,
    StudyResponseEvaluation,
    StudySession,
    StudyStyleProfile,
    UserProfile,
)
from emmaus.providers.llm import LLMProviderRegistry
from emmaus.services.study import StudyService
from emmaus.services.text import TextSourceService

PASSAGE_REVISIT_COOLDOWN = timedelta(days=2)


def _reference(book: str, chapter: int, start_verse: int, end_verse: int | None = None) -> PassageReference:
    return PassageReference(book=book, chapter=chapter, start_verse=start_verse, end_verse=end_verse)


def _themed_reference(
    book: str,
    chapter: int,
    start_verse: int,
    *rest: object,
) -> dict[str, object]:
    end_verse: int | None = None
    themes: tuple[str, ...]
    if rest and isinstance(rest[0], int):
        end_verse = rest[0]
        themes = tuple(str(theme) for theme in rest[1:])
    else:
        themes = tuple(str(theme) for theme in rest)
    return {"reference": _reference(book, chapter, start_verse, end_verse), "themes": themes}


CURATED_PASSAGE_LIBRARY: dict[str, list[dict[str, object]]] = {
    "consistency": [
        _themed_reference("Psalm", 23, 1, 3, "encouragement", "rest", "trust", "prayer"),
        _themed_reference("Matthew", 11, 28, 30, "encouragement", "rest", "burden", "prayer"),
        _themed_reference("Hebrews", 4, 14, 16, "prayer", "help", "assurance", "trust"),
        _themed_reference("Psalm", 27, 13, 14, "encouragement", "trust", "courage", "waiting"),
        _themed_reference("Isaiah", 40, 29, 31, "encouragement", "strength", "waiting"),
        _themed_reference("Lamentations", 3, 22, 24, "hope", "mercy", "encouragement", "restart"),
        _themed_reference("Psalm", 1, 1, 3, "steadiness", "scripture", "rhythm"),
        _themed_reference("Galatians", 6, 9, 10, "perseverance", "service", "obedience"),
    ],
    "application": [
        _themed_reference("James", 1, 22, 25, "obedience", "follow_through", "scripture"),
        _themed_reference("Micah", 6, 8, "obedience", "justice", "mercy", "humility"),
        _themed_reference("Colossians", 3, 12, 17, "compassion", "community", "speech", "obedience"),
        _themed_reference("Luke", 6, 46, 49, "obedience", "foundation", "follow_through"),
        _themed_reference("Romans", 12, 9, 13, "love", "service", "prayer"),
        _themed_reference("Ephesians", 4, 29, 32, "speech", "forgiveness", "community"),
        _themed_reference("Philippians", 2, 3, 5, "humility", "service", "love"),
        _themed_reference("1 John", 3, 16, 18, "love", "service", "generosity"),
    ],
    "comprehension": [
        _themed_reference("Luke", 24, 13, 17, "understanding", "discouragement", "christ_centered"),
        _themed_reference("Luke", 24, 25, 27, "understanding", "scripture", "christ_centered"),
        _themed_reference("John", 3, 16, 17, "gospel", "love", "identity", "christ_centered"),
        _themed_reference("Nehemiah", 8, 8, 10, "scripture", "understanding", "joy"),
        _themed_reference("Mark", 4, 35, 41, "trust", "fear", "christ_centered"),
        _themed_reference("Psalm", 119, 33, 37, "scripture", "understanding", "obedience"),
        _themed_reference("Acts", 8, 30, 35, "scripture", "understanding", "christ_centered"),
        _themed_reference("2 Timothy", 3, 14, 17, "scripture", "understanding", "equipping"),
    ],
    "growth": [
        _themed_reference("John", 15, 1, 5, "abiding", "fruitfulness", "identity"),
        _themed_reference("Philippians", 3, 7, 14, "growth", "pursuit", "endurance"),
        _themed_reference("Hebrews", 12, 1, 3, "endurance", "suffering", "christ_centered"),
        _themed_reference("Romans", 8, 31, 39, "assurance", "identity", "suffering"),
        _themed_reference("2 Peter", 1, 3, 8, "growth", "diligence", "holiness"),
        _themed_reference("Colossians", 2, 6, 7, "rootedness", "identity", "thankfulness"),
        _themed_reference("Ephesians", 3, 16, 19, "identity", "love", "strength"),
        _themed_reference("Galatians", 5, 22, 25, "spirit", "fruit", "holiness"),
    ],
}

CURATED_PASSAGE_BANK: dict[str, list[PassageReference]] = {
    focus: [entry["reference"] for entry in entries]
    for focus, entries in CURATED_PASSAGE_LIBRARY.items()
}

BASE_THEME_WEIGHTS: dict[str, Counter[str]] = {
    "consistency": Counter({"encouragement": 2, "rest": 2, "steadiness": 2, "trust": 1, "prayer": 1, "waiting": 1}),
    "application": Counter({"obedience": 3, "follow_through": 2, "service": 1, "love": 1, "humility": 1, "speech": 1}),
    "comprehension": Counter({"understanding": 3, "scripture": 2, "christ_centered": 2, "trust": 1}),
    "growth": Counter({"growth": 2, "identity": 2, "abiding": 1, "endurance": 1, "holiness": 1, "love": 1}),
}

THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "prayer": ("pray", "prayer", "intercede"),
    "encouragement": ("encouragement", "comfort", "hope", "weary", "burden", "overwhelmed", "peace"),
    "obedience": ("obey", "obedience", "doer", "action", "follow-through", "follow through", "next step"),
    "follow_through": ("follow-through", "follow through", "finish", "complete", "carry forward"),
    "service": ("serve", "service", "care", "kindness", "hospitality", "generosity", "someone else"),
    "love": ("love", "compassion", "mercy", "forgive", "forgiveness"),
    "humility": ("humble", "humility", "lowly"),
    "speech": ("speech", "words", "tongue", "talk", "speak"),
    "understanding": ("understand", "understanding", "clarity", "meaning", "interpret", "interpretation"),
    "scripture": ("scripture", "word", "passage", "text", "reading", "read"),
    "christ_centered": ("christ", "jesus", "gospel", "cross", "resurrection"),
    "identity": ("identity", "assurance", "beloved", "adopted", "in christ", "love of god"),
    "trust": ("trust", "rest", "wait", "waiting", "fear", "peace"),
    "endurance": ("endure", "endurance", "persevere", "perseverance", "patience", "steady", "rhythm"),
    "suffering": ("suffer", "suffering", "pain", "grief", "storm", "discouraged", "anxious", "stressed"),
    "strength": ("strength", "strong", "faint", "weak"),
    "growth": ("grow", "growth", "maturity", "deeper", "challenge"),
    "holiness": ("holy", "godliness", "purity", "fruit"),
    "abiding": ("abide", "abiding", "remain", "rooted"),
    "hope": ("hope", "mercies", "faithfulness"),
    "joy": ("joy", "glad", "rejoice"),
}


class PersonalizationService:
    def __init__(
        self,
        study_service: StudyService,
        text_service: TextSourceService,
        llm_registry: LLMProviderRegistry,
    ) -> None:
        self.study_service = study_service
        self.text_service = text_service
        self.llm_registry = llm_registry

    def build_gap_report(self, user_id: str, cache: dict[str, object] | None = None) -> StudyGapReport:
        cache = self._resolve_cache(cache)
        cache_key = f"gap_report:{user_id}"
        if cache_key in cache:
            return cache[cache_key]  # type: ignore[return-value]

        profile = self._get_cached(cache, f"profile:{user_id}", lambda: self.study_service.get_profile(user_id))
        pattern_summary = self._get_cached(
            cache,
            f"pattern_summary:{user_id}",
            lambda: self.study_service.summarize_patterns(user_id),
        )
        recent_evaluations = self._evaluate_recent_responses(user_id, cache=cache)
        open_action_items = self._get_cached(
            cache,
            f"open_action_items:{user_id}",
            lambda: self.study_service.list_action_items(user_id, status="open"),
        )
        events = self._get_cached(cache, f"events:{user_id}", lambda: self.study_service.list_events(user_id))
        latest_mood = self._get_cached(
            cache,
            f"latest_mood:{user_id}",
            lambda: self.study_service.get_latest_mood_checkin(user_id),
        )
        memory_summary = self._get_cached(
            cache,
            f"memory_summary:{user_id}",
            lambda: self.study_service.summarize_spiritual_memory(user_id),
        )

        observed_patterns: list[str] = []
        focus_votes: Counter[str] = Counter()

        comprehension_gap = 0.2
        comprehension_evaluations = [
            evaluation
            for _, _, evaluation in recent_evaluations
            if evaluation.question_type in {"observation", "interpretation", "reflection"}
        ]
        if comprehension_evaluations:
            average_comprehension = self._average_score(comprehension_evaluations, "comprehension_score")
            average_clarity = self._average_score(comprehension_evaluations, "clarity_score")
            comprehension_gap = max(0.05, 1 - ((average_comprehension * 0.75) + (average_clarity * 0.25)))
            if average_comprehension < 0.55:
                self._append_pattern(
                    observed_patterns,
                    "Recent answers suggest the user needs to slow down and understand the passage more clearly before moving on.",
                )
            elif average_comprehension < 0.72:
                self._append_pattern(
                    observed_patterns,
                    "Recent answers show partial understanding that could grow with stronger observation and interpretation.",
                )
            self._merge_patterns(observed_patterns, comprehension_evaluations)
            focus_votes.update(evaluation.recommended_focus for evaluation in comprehension_evaluations)
        elif profile.completed_sessions > 0:
            comprehension_gap = 0.45
            self._append_pattern(observed_patterns, "Recent sessions do not yet show enough evidence of understanding to guide the next step confidently.")

        application_gap = 0.22
        application_evaluations = [
            evaluation
            for _, _, evaluation in recent_evaluations
            if evaluation.question_type in {"application", "reflection"}
        ]
        if application_evaluations:
            average_application = self._average_score(application_evaluations, "application_score")
            average_clarity = self._average_score(application_evaluations, "clarity_score")
            application_gap = max(0.08, 1 - ((average_application * 0.8) + (average_clarity * 0.2)))
            if average_application < 0.58:
                self._append_pattern(
                    observed_patterns,
                    "Recent responses point in a meaningful direction, but they still need clearer real-world follow-through.",
                )
            self._merge_patterns(observed_patterns, application_evaluations)
            focus_votes.update(evaluation.recommended_focus for evaluation in application_evaluations)

        if open_action_items:
            application_gap = min(1.0, max(application_gap + min(0.4, 0.15 * len(open_action_items)), 0.72))
            self._append_pattern(observed_patterns, "There are unfinished action items from prior sessions.")

        consistency_gap = 0.1
        if profile.completed_sessions == 0:
            consistency_gap = 0.45
            self._append_pattern(observed_patterns, "The user is still building an initial study rhythm.")
        elif profile.current_streak == 0:
            consistency_gap += 0.45
            self._append_pattern(observed_patterns, "The current study rhythm has broken and needs a gentle restart.")
        elif profile.current_streak == 1:
            consistency_gap += 0.2
        if profile.last_completed_on is not None:
            days_since_last = (datetime.now(UTC).date() - profile.last_completed_on).days
            if days_since_last >= 3:
                consistency_gap = min(1.0, consistency_gap + 0.25)
                self._append_pattern(observed_patterns, "Several days have passed since the last completed session.")

        low_engagement_events = [event for event in events if event.engagement_score <= 2 and event.event_type != "mood_logged"]
        if low_engagement_events:
            comprehension_gap = min(1.0, comprehension_gap + 0.08)
            consistency_gap = min(1.0, consistency_gap + 0.12)
            self._append_pattern(observed_patterns, "Low-engagement sessions suggest the next plan should be simpler or more focused.")

        if latest_mood is not None:
            if latest_mood.mood in {"anxious", "stressed", "discouraged"}:
                consistency_gap = min(1.0, consistency_gap + 0.15)
                application_gap = min(1.0, application_gap + 0.08)
                self._append_pattern(observed_patterns, f"Recent mood check-in shows the user feels {latest_mood.mood}.")
            elif latest_mood.mood in {"encouraged", "peaceful"} and pattern_summary.average_engagement >= 4:
                self._append_pattern(observed_patterns, "Recent mood check-in suggests the user may be ready for a deeper challenge.")

        if memory_summary.memory_count > 0:
            if memory_summary.latest_summary:
                self._append_pattern(observed_patterns, f"Recent spiritual thread: {memory_summary.latest_summary}")
            for area in memory_summary.growth_areas[:2]:
                self._append_pattern(observed_patterns, f"Emmaus has been tracking growth in {area}.")
            for theme in memory_summary.recurring_themes[:2]:
                self._append_pattern(observed_patterns, f"Recurring theme in recent sessions: {theme}.")

        if focus_votes["comprehension"] > focus_votes["application"]:
            comprehension_gap = min(1.0, comprehension_gap + 0.05)
        elif focus_votes["application"] > focus_votes["comprehension"]:
            application_gap = min(1.0, application_gap + 0.05)

        comprehension_gap = round(min(1.0, comprehension_gap), 2)
        application_gap = round(min(1.0, application_gap), 2)
        consistency_gap = round(min(1.0, consistency_gap), 2)

        focus_area = max(
            ("application", application_gap),
            ("comprehension", comprehension_gap),
            ("consistency", consistency_gap),
            key=lambda item: item[1],
        )[0]
        if (
            max(comprehension_gap, application_gap, consistency_gap) < 0.35
            and pattern_summary.average_engagement >= 4
            and focus_votes["growth"] >= max(1, focus_votes["comprehension"], focus_votes["application"])
        ):
            focus_area = "growth"
            self._append_pattern(observed_patterns, "Recent engagement and response quality are healthy enough to support a deeper challenge.")

        report = StudyGapReport(
            user_id=user_id,
            comprehension_gap=comprehension_gap,
            application_gap=application_gap,
            consistency_gap=consistency_gap,
            focus_area=focus_area,
            observed_patterns=observed_patterns[:5],
        )
        cache[cache_key] = report
        return report

    def build_recommendation(self, user_id: str, cache: dict[str, object] | None = None) -> StudyRecommendation:
        cache = self._resolve_cache(cache)
        cache_key = f"recommendation:{user_id}"
        if cache_key in cache:
            return cache[cache_key]  # type: ignore[return-value]

        profile = self._get_cached(cache, f"profile:{user_id}", lambda: self.study_service.get_profile(user_id))
        pattern_summary = self._get_cached(
            cache,
            f"pattern_summary:{user_id}",
            lambda: self.study_service.summarize_patterns(user_id),
        )
        gap_report = self.build_gap_report(user_id, cache=cache)
        latest_mood = self._get_cached(
            cache,
            f"latest_mood:{user_id}",
            lambda: self.study_service.get_latest_mood_checkin(user_id),
        )
        memory_summary = self._get_cached(
            cache,
            f"memory_summary:{user_id}",
            lambda: self.study_service.summarize_spiritual_memory(user_id),
        )

        focus = gap_report.focus_area
        lead_pattern = gap_report.observed_patterns[0] if gap_report.observed_patterns else None
        reference, revisit_reason = self._select_reference_choice(user_id, focus, cache=cache)
        if focus == "consistency":
            guide_mode = "coach"
            entry_point = "help me restart after missing a few days"
            minutes = min(15, pattern_summary.recommended_session_minutes)
            reason = "A gentle restart will help rebuild rhythm without overwhelming the user."
            suggested_action = "Finish one short session and keep one practical encouragement in view today."
        elif focus == "application":
            guide_mode = "coach"
            entry_point = "continue where I left off"
            minutes = max(10, min(20, pattern_summary.recommended_session_minutes))
            reason = "Recent study shows the user needs stronger follow-through and clearer next steps."
            suggested_action = "Focus the next session on one concrete act of obedience, encouragement, or prayer."
        elif focus == "comprehension":
            guide_mode = "guide"
            entry_point = "I want to understand this passage better"
            minutes = max(15, pattern_summary.recommended_session_minutes)
            reason = "Recent answers suggest the user needs more interpretive depth and clearer understanding."
            suggested_action = "Slow down the next session and strengthen observation and interpretation before moving on."
        else:
            guide_mode = "challenger"
            entry_point = "I want a deeper challenge"
            minutes = max(20, pattern_summary.recommended_session_minutes)
            reason = "Current patterns are healthy enough to push into deeper reflection and challenge."
            suggested_action = "Use the next session to confront assumptions and pursue a more demanding application."

        if revisit_reason:
            reason = f"{revisit_reason} {reason}"

        if lead_pattern is not None:
            reason = f"{reason} {lead_pattern}"

        if memory_summary.memory_count > 0:
            if focus in {"application", "comprehension", "growth"} and memory_summary.carry_forward_prompt:
                entry_point = memory_summary.carry_forward_prompt[:120]
            if memory_summary.latest_summary:
                reason = f"{reason} Building on a recent thread: {memory_summary.latest_summary}"
            if memory_summary.growth_areas and focus != "consistency":
                suggested_action = f"Return to this growth edge next: {memory_summary.growth_areas[0]}."

        if profile.preferences.preferred_guide_mode == "peer" and focus in {"consistency", "application"}:
            guide_mode = "peer"

        if latest_mood is not None:
            if latest_mood.mood in {"anxious", "stressed", "discouraged"}:
                reference, revisit_reason = self._select_reference_choice(
                    user_id,
                    "consistency",
                    cache=cache,
                    preferred_themes=Counter({"encouragement": 4, "rest": 3, "prayer": 3, "trust": 2, "hope": 2}),
                )
                guide_mode = "peer" if profile.preferences.preferred_guide_mode == "peer" else "guide"
                entry_point = "I need encouragement"
                reason = "Recent mood signals suggest the next session should steady and encourage the user before pressing harder."
                suggested_action = "Keep the next session gentle, grounded, and prayerful."
            if latest_mood.energy == "low":
                minutes = max(5, min(minutes, 10))
            elif latest_mood.energy == "high" and focus == "growth":
                minutes = min(30, minutes + 5)

        recommendation = StudyRecommendation(
            user_id=user_id,
            focus_area=focus,
            recommended_reference=reference,
            recommended_guide_mode=guide_mode,
            recommended_minutes=minutes,
            recommended_entry_point=entry_point,
            reason=reason,
            suggested_action=suggested_action,
            gap_report=gap_report,
        )
        cache[cache_key] = recommendation
        return recommendation

    def build_style_profile(
        self,
        user_id: str,
        recommendation: StudyRecommendation | None = None,
        cache: dict[str, object] | None = None,
    ) -> StudyStyleProfile:
        cache = self._resolve_cache(cache)
        profile = self._get_cached(cache, f"profile:{user_id}", lambda: self.study_service.get_profile(user_id))
        pattern_summary = self._get_cached(
            cache,
            f"pattern_summary:{user_id}",
            lambda: self.study_service.summarize_patterns(user_id),
        )
        latest_mood = self._get_cached(
            cache,
            f"latest_mood:{user_id}",
            lambda: self.study_service.get_latest_mood_checkin(user_id),
        )
        open_action_items = self._get_cached(
            cache,
            f"open_action_items:{user_id}",
            lambda: self.study_service.list_action_items(user_id, status="open"),
        )
        recommendation = recommendation or self.build_recommendation(user_id, cache=cache)

        question_style = profile.preferences.preferred_question_style
        guidance_tone = profile.preferences.preferred_guidance_tone
        reasons: list[str] = []

        if latest_mood is not None and latest_mood.mood in {"anxious", "stressed", "discouraged"}:
            guidance_tone = "warm"
            if recommendation.focus_area != "application":
                question_style = "reflective"
            reasons.append("Recent mood signals call for gentler language and a calmer pace.")
        elif recommendation.focus_area == "application" or open_action_items:
            question_style = "practical"
            reasons.append("Recent follow-through patterns call for clearer next-step language.")
        elif recommendation.focus_area == "growth" and pattern_summary.average_engagement >= 4:
            question_style = "probing"
            if guidance_tone == "steady":
                guidance_tone = "direct"
            reasons.append("Recent engagement suggests the user can handle deeper and more direct questions.")
        elif recommendation.focus_area == "comprehension":
            question_style = "reflective"
            reasons.append("Current study needs slower observation and clearer understanding.")
        elif recommendation.focus_area == "consistency" and pattern_summary.average_engagement <= 3:
            question_style = "concise"
            reasons.append("The next session should feel simple enough to finish without friction.")

        if pattern_summary.average_engagement <= 2.5 and question_style == "probing":
            question_style = "concise"
            reasons.append("Lower recent engagement means shorter prompts will likely land better.")

        if not reasons:
            reasons.append("Emmaus is using the saved guide preferences as the baseline voice for this session.")

        return StudyStyleProfile(
            user_id=user_id,
            question_style=question_style,
            guidance_tone=guidance_tone,
            reason=" ".join(reasons[:2]),
        )

    def preview_nudge(
        self,
        user_id: str,
        preview_at: datetime | None = None,
        cache: dict[str, object] | None = None,
    ) -> NudgePreview:
        cache = self._resolve_cache(cache)
        recommendation = self.build_recommendation(user_id, cache=cache)
        profile = self._get_cached(cache, f"profile:{user_id}", lambda: self.study_service.get_profile(user_id))
        latest_mood = self._get_cached(
            cache,
            f"latest_mood:{user_id}",
            lambda: self.study_service.get_latest_mood_checkin(user_id),
        )
        open_action_items = self._get_cached(
            cache,
            f"open_action_items:{user_id}",
            lambda: self.study_service.list_action_items(user_id, status="open"),
        )
        recent_action_items = self._get_cached(
            cache,
            f"recent_action_items:{user_id}",
            lambda: self.study_service.list_action_items(user_id),
        )
        memory_summary = self._get_cached(
            cache,
            f"memory_summary:{user_id}",
            lambda: self.study_service.summarize_spiritual_memory(user_id),
        )
        recent_follow_through = self._latest_completed_follow_through(recent_action_items)

        if latest_mood is not None and latest_mood.mood in {"anxious", "stressed", "discouraged"}:
            nudge_type = "encouragement"
            title = "A gentle moment with Scripture"
            message = "A short, steady session may help you reconnect with Christ without adding pressure today."
        elif open_action_items:
            nudge_type = "follow_through"
            title = "Follow through on your last step"
            message = "Your last session already surfaced a practical next step. Review it and take one small action today."
        elif recent_follow_through is not None and memory_summary.memory_count > 0:
            nudge_type = "theme"
            title = "Build on what already landed"
            message = self._build_completed_follow_through_nudge(
                recent_follow_through,
                memory_summary.carry_forward_prompt,
                recommendation.suggested_action,
            )
        elif profile.current_streak == 0:
            nudge_type = "restart"
            title = "Begin again today"
            message = "You do not need to catch up. Start with one small session and let the rhythm begin again."
        elif memory_summary.memory_count > 0 and memory_summary.recurring_themes:
            nudge_type = "theme"
            title = "Return to what Christ has been surfacing"
            message = f"Emmaus has noticed a recurring thread around {memory_summary.recurring_themes[0]}. Revisit it with one focused session today."
        elif profile.current_streak >= 1:
            nudge_type = "momentum"
            title = "Keep your rhythm going"
            message = "You already have momentum. A short session today will keep the pattern alive."
        else:
            nudge_type = "theme"
            title = "Return to a meaningful thread"
            message = "A focused session can help you keep growing in the area Emmaus has been tracking for you."

        timing_decision, scheduled_for, timing_reason, local_timezone = self._decide_nudge_timing(profile, preview_at)

        return NudgePreview(
            user_id=user_id,
            nudge_type=nudge_type,
            title=title,
            message=message,
            recommended_entry_point=recommendation.recommended_entry_point,
            recommended_minutes=recommendation.recommended_minutes,
            recommended_guide_mode=recommendation.recommended_guide_mode,
            recommendation=recommendation,
            timing_decision=timing_decision,
            timing_reason=timing_reason,
            scheduled_for=scheduled_for,
            local_timezone=local_timezone,
        )

    def _latest_completed_follow_through(self, action_items):
        return next(
            (
                item
                for item in action_items
                if item.status == "completed" and (item.follow_up_outcome or item.completed_at is not None)
            ),
            None,
        )

    def _build_completed_follow_through_nudge(
        self,
        action_item,
        carry_forward_prompt: str | None,
        suggested_action: str,
    ) -> str:
        outcome = action_item.follow_up_outcome or "completed"
        if outcome == "prayed_through":
            lead = f"You already carried '{action_item.title}' into prayer."
        elif outcome == "discussed_with_someone":
            lead = f"You already talked through '{action_item.title}' with someone else."
        elif outcome == "partially_completed":
            lead = f"You already started '{action_item.title}'."
        else:
            lead = f"You already followed through on '{action_item.title}'."

        next_step = carry_forward_prompt or suggested_action or "Return to that same thread and ask what Christ is inviting next."
        return f"{lead} {next_step}"

    def build_nudge_delivery_plan(
        self,
        user_id: str,
        preview_at: datetime | None = None,
        cache: dict[str, object] | None = None,
    ) -> NudgeDeliveryPlan:
        cache = self._resolve_cache(cache)
        preview = self.preview_nudge(user_id, preview_at=preview_at, cache=cache)
        if preview.timing_decision == "now":
            deliver_at = preview_at or datetime.now(UTC)
            return NudgeDeliveryPlan(
                user_id=user_id,
                delivery_status="send_now",
                delivery_channel="push",
                deliver_at=deliver_at,
                fallback_at=deliver_at,
                idempotency_key=self._idempotency_key(user_id, preview, deliver_at),
                reason="The user is inside an allowed study window, so this notification can be sent immediately.",
                nudge=preview,
            )
        if preview.timing_decision == "later_today":
            deliver_at = preview.scheduled_for
            return NudgeDeliveryPlan(
                user_id=user_id,
                delivery_status="scheduled",
                delivery_channel="push",
                deliver_at=deliver_at,
                fallback_at=deliver_at,
                idempotency_key=self._idempotency_key(user_id, preview, deliver_at),
                reason="The nudge should wait until the user's preferred study window opens later today.",
                nudge=preview,
            )

        fallback_at = self._next_delivery_candidate(self.study_service.get_profile(user_id), preview_at)
        return NudgeDeliveryPlan(
            user_id=user_id,
            delivery_status="suppressed",
            delivery_channel="in_app",
            deliver_at=None,
            fallback_at=fallback_at,
            idempotency_key=self._idempotency_key(user_id, preview, fallback_at),
            reason="A push notification should be held because today is outside the user's allowed study window or day.",
            nudge=preview,
        )

    def _evaluate_recent_responses(
        self,
        user_id: str,
        limit_sessions: int = 5,
        cache: dict[str, object] | None = None,
    ) -> list[tuple[StudySession, SessionResponse, StudyResponseEvaluation]]:
        cache = self._resolve_cache(cache)
        cache_key = f"recent_evaluations:{user_id}:{limit_sessions}"
        if cache_key in cache:
            return cache[cache_key]  # type: ignore[return-value]
        evaluated_responses: list[tuple[StudySession, SessionResponse, StudyResponseEvaluation]] = []
        sessions = self.study_service.list_sessions(user_id, status="completed")[:limit_sessions]
        for session in sessions:
            passage = self.text_service.get_passage(session.reference, session.text_source_id)
            provider = self.llm_registry.get(session.llm_source_id)
            passage_reference = self._format_reference(session.reference)
            for response in self.study_service.list_session_responses(session.session_id):
                evaluation = provider.evaluate_response(
                    passage_reference=passage_reference,
                    passage_text=passage.text,
                    question=response.question,
                    question_type=response.question_type,
                    response_text=response.response_text,
                )
                evaluated_responses.append((session, response, evaluation))
        cache[cache_key] = evaluated_responses
        return evaluated_responses

    def _average_score(self, evaluations: list[StudyResponseEvaluation], attribute: str) -> float:
        return round(sum(getattr(evaluation, attribute) for evaluation in evaluations) / len(evaluations), 2)

    def _append_pattern(self, observed_patterns: list[str], pattern: str) -> None:
        if pattern and pattern not in observed_patterns:
            observed_patterns.append(pattern)

    def _merge_patterns(self, observed_patterns: list[str], evaluations: list[StudyResponseEvaluation]) -> None:
        for evaluation in evaluations:
            for pattern in evaluation.observed_patterns:
                self._append_pattern(observed_patterns, pattern)

    def _format_reference(self, reference: PassageReference) -> str:
        ending = f"-{reference.end_verse}" if reference.end_verse else ""
        return f"{reference.book} {reference.chapter}:{reference.start_verse}{ending}"

    def _select_reference_for_focus(
        self,
        user_id: str,
        focus: str,
        cache: dict[str, object] | None = None,
        preferred_themes: Counter[str] | None = None,
    ) -> PassageReference:
        reference, _ = self._select_reference_choice(
            user_id,
            focus,
            cache=cache,
            preferred_themes=preferred_themes,
        )
        return reference

    def _select_reference_choice(
        self,
        user_id: str,
        focus: str,
        cache: dict[str, object] | None = None,
        preferred_themes: Counter[str] | None = None,
    ) -> tuple[PassageReference, str | None]:
        cache = self._resolve_cache(cache)
        library = CURATED_PASSAGE_LIBRARY.get(focus) or CURATED_PASSAGE_LIBRARY["growth"]
        seen_records = {
            self._format_reference(record.reference): record
            for record in self.study_service.list_seen_passages(user_id, focus)
        }
        all_seen_records = self._get_cached(
            cache,
            f"seen_passages:{user_id}:all",
            lambda: self.study_service.list_seen_passages(user_id),
        )
        recent_cutoff = datetime.now(UTC) - PASSAGE_REVISIT_COOLDOWN
        recent_reference_keys = {
            self._format_reference(record.reference)
            for record in all_seen_records
            if record.last_seen_at >= recent_cutoff
        }
        most_recent_record = max(all_seen_records, key=lambda record: record.last_seen_at, default=None)
        theme_weights = self._build_theme_weights(user_id, focus, cache=cache, preferred_themes=preferred_themes)
        unseen_entries = [entry for entry in library if self._format_reference(entry["reference"]) not in seen_records]
        unseen_without_recent = [
            entry for entry in unseen_entries if self._format_reference(entry["reference"]) not in recent_reference_keys
        ]
        if unseen_without_recent:
            return self._choose_best_entry(unseen_without_recent, theme_weights, library)["reference"], None
        if unseen_entries:
            chosen_entry = self._choose_best_entry(unseen_entries, theme_weights, library)
            chosen_reference = chosen_entry["reference"]
            return chosen_reference, self._build_revisit_reason(chosen_reference, most_recent_record)

        top_score = max(self._score_entry_themes(entry, theme_weights) for entry in library)
        top_entries = [entry for entry in library if self._score_entry_themes(entry, theme_weights) == top_score]
        candidate_entries = [
            entry for entry in top_entries if self._format_reference(entry["reference"]) not in recent_reference_keys
        ] or top_entries
        chosen_entry = min(
            candidate_entries,
            key=lambda entry: (
                seen_records[self._format_reference(entry["reference"])].session_count,
                seen_records[self._format_reference(entry["reference"])].last_seen_at,
                library.index(entry),
            ),
        )
        chosen_reference = chosen_entry["reference"]
        revisit_reason = None
        if self._format_reference(chosen_reference) in recent_reference_keys:
            revisit_reason = self._build_revisit_reason(chosen_reference, most_recent_record)
        return chosen_reference, revisit_reason

    def _build_revisit_reason(self, reference: PassageReference, most_recent_record: object | None) -> str:
        reference_label = self._format_reference(reference)
        if most_recent_record is not None and self._format_reference(most_recent_record.reference) == reference_label:
            return (
                f"Emmaus is bringing you back to {reference_label} because your most recent session and next step "
                "are still pointing to the same growth edge."
            )
        return f"Emmaus is revisiting {reference_label} because it still speaks directly to the thread it is carrying forward."

    def _build_theme_weights(
        self,
        user_id: str,
        focus: str,
        cache: dict[str, object] | None = None,
        preferred_themes: Counter[str] | None = None,
    ) -> Counter[str]:
        cache = self._resolve_cache(cache)
        weights = Counter(BASE_THEME_WEIGHTS.get(focus, {}))
        if preferred_themes:
            weights.update(preferred_themes)

        latest_mood = self._get_cached(
            cache,
            f"latest_mood:{user_id}",
            lambda: self.study_service.get_latest_mood_checkin(user_id),
        )
        open_action_items = self._get_cached(
            cache,
            f"open_action_items:{user_id}",
            lambda: self.study_service.list_action_items(user_id, status="open"),
        )
        active_prayer_items = self._get_cached(
            cache,
            f"active_prayer_items:{user_id}",
            lambda: self.study_service.list_prayer_items(user_id, status="active"),
        )
        memory_summary = self._get_cached(
            cache,
            f"memory_summary:{user_id}",
            lambda: self.study_service.summarize_spiritual_memory(user_id),
        )

        if latest_mood is not None:
            if latest_mood.mood in {"anxious", "stressed", "discouraged"}:
                weights.update(Counter({"encouragement": 3, "trust": 2, "rest": 2, "prayer": 2, "hope": 1, "suffering": 1}))
            elif latest_mood.mood in {"peaceful", "encouraged"}:
                weights.update(Counter({"growth": 1, "endurance": 1, "love": 1}))

            if latest_mood.energy == "low":
                weights.update(Counter({"rest": 2, "encouragement": 1, "steadiness": 1}))
            elif latest_mood.energy == "high":
                weights.update(Counter({"growth": 1, "endurance": 1}))

            self._apply_theme_keywords(weights, latest_mood.notes)

        if open_action_items:
            weights.update(Counter({"obedience": 3, "follow_through": 3, "service": 1, "prayer": 1}))
            for item in open_action_items[:3]:
                self._apply_theme_keywords(weights, f"{item.title} {item.detail}")

        if active_prayer_items:
            weights.update(Counter({"prayer": 3, "trust": 1, "encouragement": 1}))
            for item in active_prayer_items[:3]:
                self._apply_theme_keywords(weights, f"{item.title} {item.detail}")

        if memory_summary.memory_count > 0:
            self._apply_theme_keywords(weights, memory_summary.latest_summary)
            self._apply_theme_keywords(weights, memory_summary.carry_forward_prompt)
            for theme in memory_summary.recurring_themes[:4]:
                self._apply_theme_keywords(weights, theme)
            for area in memory_summary.growth_areas[:4]:
                self._apply_theme_keywords(weights, area)

        return weights

    def _apply_theme_keywords(self, weights: Counter[str], text: str | None) -> None:
        if not text:
            return
        lowered = text.lower()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                weights[theme] += 1

    def _choose_best_entry(
        self,
        entries: list[dict[str, object]],
        theme_weights: Counter[str],
        library: list[dict[str, object]],
    ) -> dict[str, object]:
        return max(
            entries,
            key=lambda entry: (
                self._score_entry_themes(entry, theme_weights),
                -library.index(entry),
            ),
        )

    def _score_entry_themes(self, entry: dict[str, object], theme_weights: Counter[str]) -> int:
        return sum(theme_weights.get(theme, 0) for theme in entry.get("themes", ()))

    def _decide_nudge_timing(
        self,
        profile: UserProfile,
        preview_at: datetime | None,
    ) -> tuple[str, datetime | None, str, str]:
        timezone_name = profile.preferences.timezone or "UTC"
        if timezone_name in {"UTC", "Etc/UTC"}:
            zone = UTC
            timezone_name = "UTC"
        else:
            try:
                zone = ZoneInfo(timezone_name)
            except ZoneInfoNotFoundError:
                zone = UTC
                timezone_name = "UTC"

        base_time = preview_at or datetime.now(UTC)
        if base_time.tzinfo is None:
            base_time = base_time.replace(tzinfo=UTC)
        local_now = base_time.astimezone(zone)

        if self._outside_preferred_days(profile, local_now):
            return "not_today", None, "Today is outside the user's preferred study days.", timezone_name

        quiet_start = self._parse_time(profile.preferences.quiet_hours_start)
        quiet_end = self._parse_time(profile.preferences.quiet_hours_end)
        window_start = self._parse_time(profile.preferences.preferred_study_window_start)
        window_end = self._parse_time(profile.preferences.preferred_study_window_end)

        in_quiet = self._in_window(local_now.timetz().replace(tzinfo=None), quiet_start, quiet_end)
        if in_quiet:
            quiet_end_dt = self._next_window_end(local_now, quiet_start, quiet_end)
            candidate = quiet_end_dt
            if window_start is not None and window_end is not None:
                window_start_dt = local_now.replace(hour=window_start.hour, minute=window_start.minute, second=0, microsecond=0)
                if candidate < window_start_dt:
                    candidate = window_start_dt
                if not self._same_local_day(local_now, candidate):
                    return "not_today", None, "Quiet hours cover the rest of today's available study time.", timezone_name
                if not self._can_fit_in_window(candidate, window_start, window_end):
                    return "not_today", None, "Quiet hours push the nudge outside today's preferred study window.", timezone_name
            if self._same_local_day(local_now, candidate):
                return "later_today", candidate, "It is currently quiet hours, so the nudge should wait.", timezone_name
            return "not_today", None, "Quiet hours push the next allowed nudge into another day.", timezone_name

        if window_start is None or window_end is None:
            return "now", None, "No preferred study window is configured, so the nudge can be sent now.", timezone_name

        current_time = local_now.timetz().replace(tzinfo=None)
        if self._in_window(current_time, window_start, window_end):
            return "now", None, "The current time falls inside the user's preferred study window.", timezone_name

        window_start_dt = local_now.replace(hour=window_start.hour, minute=window_start.minute, second=0, microsecond=0)
        window_end_dt = self._next_window_end(local_now, window_start, window_end)
        if current_time < window_start and self._same_local_day(local_now, window_start_dt):
            return "later_today", window_start_dt, "The next preferred study window begins later today.", timezone_name
        if self._same_local_day(local_now, window_end_dt) and current_time < window_end:
            return "later_today", window_start_dt, "The preferred study window begins later today.", timezone_name
        return "not_today", None, "Today's preferred study window has already passed.", timezone_name

    def _next_delivery_candidate(self, profile: UserProfile, preview_at: datetime | None) -> datetime | None:
        timezone_name = profile.preferences.timezone or "UTC"
        if timezone_name in {"UTC", "Etc/UTC"}:
            zone = UTC
        else:
            try:
                zone = ZoneInfo(timezone_name)
            except ZoneInfoNotFoundError:
                zone = UTC
        base_time = preview_at or datetime.now(UTC)
        if base_time.tzinfo is None:
            base_time = base_time.replace(tzinfo=UTC)
        local_now = base_time.astimezone(zone)
        window_start = self._parse_time(profile.preferences.preferred_study_window_start) or time(hour=9, minute=0)
        quiet_start = self._parse_time(profile.preferences.quiet_hours_start)
        quiet_end = self._parse_time(profile.preferences.quiet_hours_end)
        preferred_days = {day.strip().lower() for day in profile.preferences.preferred_study_days}

        for day_offset in range(1, 8):
            candidate = (local_now + timedelta(days=day_offset)).replace(
                hour=window_start.hour,
                minute=window_start.minute,
                second=0,
                microsecond=0,
            )
            if preferred_days:
                names = {candidate.strftime("%A").lower(), candidate.strftime("%a").lower()}
                if preferred_days.isdisjoint(names):
                    continue
            candidate_time = candidate.timetz().replace(tzinfo=None)
            if self._in_window(candidate_time, quiet_start, quiet_end):
                candidate = self._next_window_end(candidate, quiet_start, quiet_end)
            return candidate.astimezone(UTC)
        return None

    def _outside_preferred_days(self, profile: UserProfile, local_now: datetime) -> bool:
        preferred_days = profile.preferences.preferred_study_days
        if not preferred_days:
            return False
        normalized = {day.strip().lower() for day in preferred_days}
        names = {local_now.strftime("%A").lower(), local_now.strftime("%a").lower()}
        return normalized.isdisjoint(names)

    def _parse_time(self, value: str | None) -> time | None:
        if value is None:
            return None
        hour, minute = value.split(":", 1)
        return time(hour=int(hour), minute=int(minute))

    def _in_window(self, current: time, start: time | None, end: time | None) -> bool:
        if start is None or end is None:
            return False
        if start == end:
            return False
        if start < end:
            return start <= current < end
        return current >= start or current < end

    def _next_window_end(self, current_dt: datetime, start: time | None, end: time | None) -> datetime:
        assert start is not None and end is not None
        candidate = current_dt.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
        if start < end:
            return candidate
        current_time = current_dt.timetz().replace(tzinfo=None)
        if current_time >= start:
            return candidate + timedelta(days=1)
        return candidate

    def _same_local_day(self, current_dt: datetime, candidate: datetime) -> bool:
        return current_dt.date() == candidate.date()

    def _can_fit_in_window(self, candidate: datetime, start: time, end: time) -> bool:
        candidate_time = candidate.timetz().replace(tzinfo=None)
        return self._in_window(candidate_time, start, end) or candidate_time == start

    def _idempotency_key(self, user_id: str, preview: NudgePreview, deliver_at: datetime | None) -> str:
        stamp = deliver_at.isoformat() if deliver_at is not None else "none"
        return f"{user_id}:{preview.nudge_type}:{preview.recommended_entry_point}:{stamp}"

    def _resolve_cache(self, cache: dict[str, object] | None) -> dict[str, object]:
        return cache if cache is not None else {}

    def _get_cached(self, cache: dict[str, object], key: str, factory):
        if key not in cache:
            cache[key] = factory()
        return cache[key]

