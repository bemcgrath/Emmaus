from __future__ import annotations

from datetime import UTC, datetime

from emmaus.domain.models import PassageReference, StudyGapReport, StudyRecommendation
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

        low_engagement_events = [event for event in events if event.engagement_score <= 2]
        if low_engagement_events:
            comprehension_gap = min(1.0, comprehension_gap + 0.1)
            consistency_gap = min(1.0, consistency_gap + 0.1)
            observed_patterns.append("Low-engagement sessions suggest the plan should be simpler or more focused.")

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
