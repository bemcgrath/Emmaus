from __future__ import annotations

from emmaus.domain.models import (
    AgentStudyResponse,
    PassageReference,
    StudyPatternSummary,
    StudyPlanStep,
    StudyQuestion,
)
from emmaus.providers.commentary import CommentaryProviderRegistry
from emmaus.providers.llm import LLMProviderRegistry
from emmaus.services.study import StudyService
from emmaus.services.text import TextSourceService


class AdaptiveStudyAgent:
    def __init__(
        self,
        study_service: StudyService,
        text_service: TextSourceService,
        commentary_registry: CommentaryProviderRegistry,
        llm_registry: LLMProviderRegistry,
        default_commentary_source: str,
    ) -> None:
        self.study_service = study_service
        self.text_service = text_service
        self.commentary_registry = commentary_registry
        self.llm_registry = llm_registry
        self.default_commentary_source = default_commentary_source

    def build_session(
        self,
        user_id: str,
        reference: PassageReference,
        text_source_id: str | None = None,
        commentary_source_id: str | None = None,
        llm_source_id: str = "local_rules",
    ) -> AgentStudyResponse:
        pattern_summary = self.study_service.summarize_patterns(user_id)
        passage = self.text_service.get_passage(reference, text_source_id)
        commentary_provider = self.commentary_registry.get(commentary_source_id or self.default_commentary_source)
        commentary = commentary_provider.get_commentary(reference)
        questions = self._generate_questions(pattern_summary)
        plan = self._generate_plan(pattern_summary, passage.text)

        prompt = (
            f"User pattern summary: {pattern_summary.model_dump_json()}\n"
            f"Passage: {passage.text}\n"
            f"Commentary: {[item.body for item in commentary]}"
        )
        guidance = self.llm_registry.get(llm_source_id).generate_guidance(prompt)

        message = (
            f"Today's study centers on {reference.book} {reference.chapter}:{reference.start_verse}"
            f"{'-' + str(reference.end_verse) if reference.end_verse else ''}. "
            f"Suggested session length: {pattern_summary.recommended_session_minutes} minutes. "
            f"{guidance}"
        )
        return AgentStudyResponse(
            message=message,
            questions=questions,
            plan=plan,
            pattern_summary=pattern_summary,
        )

    def _generate_questions(self, pattern_summary: StudyPatternSummary) -> list[StudyQuestion]:
        difficulty = pattern_summary.preferred_difficulty
        return [
            StudyQuestion(
                question="What repeated words or themes stand out in this passage?",
                type="observation",
                difficulty=difficulty,
            ),
            StudyQuestion(
                question="What does this passage reveal about God's character or intentions?",
                type="interpretation",
                difficulty=difficulty,
            ),
            StudyQuestion(
                question="What is one practical response you can make today based on this reading?",
                type="application",
                difficulty=difficulty,
            ),
        ]

    def _generate_plan(self, pattern_summary: StudyPatternSummary, passage_text: str) -> list[StudyPlanStep]:
        return [
            StudyPlanStep(
                title="Read Slowly",
                instruction=f"Read the selected text twice. Start with this excerpt: {passage_text[:180]}",
                estimated_minutes=5,
            ),
            StudyPlanStep(
                title="Reflect",
                instruction="Write one observation, one interpretation, and one application.",
                estimated_minutes=10,
            ),
            StudyPlanStep(
                title="Pray and Review",
                instruction=(
                    "Close by reviewing your notes and deciding whether the next session should stay "
                    f"at {pattern_summary.preferred_difficulty} difficulty."
                ),
                estimated_minutes=max(5, pattern_summary.recommended_session_minutes - 15),
            ),
        ]
