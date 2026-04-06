from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from emmaus.domain.models import MoodCheckIn, NudgePreview, PassageReference, StudyGapReport, StudyRecommendation, UserProfile
from emmaus.services.study import StudyService


class PersonalizationService:
    def __init__(self, study_service: StudyService) -> None:
        self.study_service = study_service

    def build_gap_report(self, user_id: str) -> StudyGapReport:
        profile = self.study_service.get_profile(user_id)
        pattern_summary = self.study_service.summarize_patterns(user_id)
        recent_responses = self.study_service.list_recent_responses(user_id)
        open_action_items = self.study_service.list_action_items(user_id, status="open")
        events = self.study_service.list_events(user_id)
        latest_mood = self.study_service.get_latest_mood_checkin(user_id)

        observed_patterns: list[str] = []

        comprehension_gap = 0.15
        comprehension_responses = [
            response for response in recent_responses if response.question_type in {"observation", "interpretation"}
        ]
        if comprehension_responses:
            short_count = sum(1 for response in comprehension_responses if len(response.response_text.strip()) < 80)
            comprehension_gap += min(0.55, short_count / max(1, len(comprehension_responses)) * 0.6)
            if short_count:
                observed_patterns.append("Recent observation or interpretation answers have been brief.")
        elif profile.completed_sessions > 0:
            comprehension_gap += 0.25
            observed_patterns.append("Recent sessions do not show enough interpretive depth yet.")

        application_gap = 0.2
        application_responses = [response for response in recent_responses if response.question_type == "application"]
        if application_responses:
            short_application = sum(1 for response in application_responses if len(response.response_text.strip()) < 90)
            application_gap += min(0.5, short_application / max(1, len(application_responses)) * 0.6)
            if short_application:
                observed_patterns.append("Application responses have often lacked concrete follow-through.")
        if open_action_items:
            application_gap += min(0.45, 0.18 * len(open_action_items))
            application_gap = max(application_gap, 0.8)
            observed_patterns.append("There are unfinished action items from prior sessions.")

        consistency_gap = 0.1
        if profile.completed_sessions == 0:
            consistency_gap = 0.45
            observed_patterns.append("The user is still building an initial study rhythm.")
        elif profile.current_streak == 0:
            consistency_gap += 0.45
            observed_patterns.append("The current study rhythm has broken and needs a gentle restart.")
        elif profile.current_streak == 1:
            consistency_gap += 0.2
        if profile.last_completed_on is not None:
            days_since_last = (datetime.now(UTC).date() - profile.last_completed_on).days
            if days_since_last >= 3:
                consistency_gap = min(1.0, consistency_gap + 0.25)
                observed_patterns.append("Several days have passed since the last completed session.")

        low_engagement_events = [event for event in events if event.engagement_score <= 2 and event.event_type != "mood_logged"]
        if low_engagement_events:
            comprehension_gap = min(1.0, comprehension_gap + 0.1)
            consistency_gap = min(1.0, consistency_gap + 0.1)
            observed_patterns.append("Low-engagement sessions suggest the plan should be simpler or more focused.")

        if latest_mood is not None:
            if latest_mood.mood in {"anxious", "stressed", "discouraged"}:
                consistency_gap = min(1.0, consistency_gap + 0.15)
                application_gap = min(1.0, application_gap + 0.1)
                observed_patterns.append(f"Recent mood check-in shows the user feels {latest_mood.mood}.")
            elif latest_mood.mood in {"encouraged", "peaceful"} and pattern_summary.average_engagement >= 4:
                observed_patterns.append("Recent mood check-in suggests the user may be ready for a deeper challenge.")

        comprehension_gap = round(min(1.0, comprehension_gap), 2)
        application_gap = round(min(1.0, application_gap), 2)
        consistency_gap = round(min(1.0, consistency_gap), 2)

        focus_area = max(
            ("application", application_gap),
            ("comprehension", comprehension_gap),
            ("consistency", consistency_gap),
            key=lambda item: item[1],
        )[0]
        if max(comprehension_gap, application_gap, consistency_gap) < 0.35 and pattern_summary.average_engagement >= 4:
            focus_area = "growth"
            observed_patterns.append("Recent engagement is healthy enough to support a deeper challenge.")

        return StudyGapReport(
            user_id=user_id,
            comprehension_gap=comprehension_gap,
            application_gap=application_gap,
            consistency_gap=consistency_gap,
            focus_area=focus_area,
            observed_patterns=observed_patterns[:5],
        )

    def build_recommendation(self, user_id: str) -> StudyRecommendation:
        profile = self.study_service.get_profile(user_id)
        pattern_summary = self.study_service.summarize_patterns(user_id)
        gap_report = self.build_gap_report(user_id)
        latest_mood = self.study_service.get_latest_mood_checkin(user_id)

        focus = gap_report.focus_area
        if focus == "consistency":
            reference = PassageReference(book="Psalm", chapter=23, start_verse=1, end_verse=3)
            guide_mode = "coach"
            entry_point = "help me restart after missing a few days"
            minutes = min(15, pattern_summary.recommended_session_minutes)
            reason = "A gentle restart will help rebuild rhythm without overwhelming the user."
            suggested_action = "Finish one short session and keep one practical encouragement in view today."
        elif focus == "application":
            reference = PassageReference(book="John", chapter=3, start_verse=16, end_verse=17)
            guide_mode = "coach"
            entry_point = "continue where I left off"
            minutes = max(10, min(20, pattern_summary.recommended_session_minutes))
            reason = "Recent study shows the user needs stronger follow-through and clearer next steps."
            suggested_action = "Focus the next session on one concrete act of obedience, encouragement, or prayer."
        elif focus == "comprehension":
            reference = PassageReference(book="John", chapter=3, start_verse=16, end_verse=17)
            guide_mode = "guide"
            entry_point = "I want to study a topic"
            minutes = max(15, pattern_summary.recommended_session_minutes)
            reason = "Recent answers suggest the user needs more interpretive depth and clearer understanding."
            suggested_action = "Slow down the next session and strengthen observation and interpretation before moving on."
        else:
            reference = PassageReference(book="John", chapter=3, start_verse=16, end_verse=17)
            guide_mode = "challenger"
            entry_point = "I want a deeper challenge"
            minutes = max(20, pattern_summary.recommended_session_minutes)
            reason = "Current patterns are healthy enough to push into deeper reflection and challenge."
            suggested_action = "Use the next session to confront assumptions and pursue a more demanding application."

        if profile.preferences.preferred_guide_mode == "peer" and focus in {"consistency", "application"}:
            guide_mode = "peer"

        if latest_mood is not None:
            if latest_mood.mood in {"anxious", "stressed", "discouraged"}:
                reference = PassageReference(book="Psalm", chapter=23, start_verse=1, end_verse=3)
                guide_mode = "peer" if profile.preferences.preferred_guide_mode == "peer" else "guide"
                entry_point = "I need encouragement"
                reason = "Recent mood signals suggest the next session should steady and encourage the user before pressing harder."
                suggested_action = "Keep the next session gentle, grounded, and prayerful."
            if latest_mood.energy == "low":
                minutes = max(5, min(minutes, 10))
            elif latest_mood.energy == "high" and focus == "growth":
                minutes = min(30, minutes + 5)

        return StudyRecommendation(
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

    def preview_nudge(self, user_id: str, preview_at: datetime | None = None) -> NudgePreview:
        recommendation = self.build_recommendation(user_id)
        profile = self.study_service.get_profile(user_id)
        latest_mood = self.study_service.get_latest_mood_checkin(user_id)
        open_action_items = self.study_service.list_action_items(user_id, status="open")

        if latest_mood is not None and latest_mood.mood in {"anxious", "stressed", "discouraged"}:
            nudge_type = "encouragement"
            title = "A gentle moment with Scripture"
            message = "A short, steady session may help you reconnect with Christ without adding pressure today."
        elif open_action_items:
            nudge_type = "follow_through"
            title = "Follow through on your last step"
            message = "Your last session already surfaced a practical next step. Review it and take one small action today."
        elif profile.current_streak == 0:
            nudge_type = "restart"
            title = "Begin again today"
            message = "You do not need to catch up. Start with one small session and let the rhythm begin again."
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

    def _decide_nudge_timing(
        self,
        profile: UserProfile,
        preview_at: datetime | None,
    ) -> tuple[str, datetime | None, str, str]:
        timezone_name = profile.preferences.timezone or "UTC"
        try:
            zone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            zone = ZoneInfo("UTC")
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
