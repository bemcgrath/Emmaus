from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from emmaus.domain.models import (
    ActionItem,
    AgentSessionCompleteResponse,
    AgentSessionStartResponse,
    AgentSessionTurnResponse,
    AgentStudyResponse,
    PassageReference,
    SessionResponse,
    StudyEvent,
    StudyPatternSummary,
    StudyPlanStep,
    StudyQuestion,
    StudySession,
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
        started = self.start_session(
            user_id=user_id,
            reference=reference,
            text_source_id=text_source_id,
            commentary_source_id=commentary_source_id,
            llm_source_id=llm_source_id,
        )
        return AgentStudyResponse(
            message=started.session.latest_message,
            questions=started.session.questions,
            plan=started.session.plan,
            pattern_summary=started.pattern_summary,
        )

    def start_session(
        self,
        user_id: str,
        reference: PassageReference | None = None,
        text_source_id: str | None = None,
        commentary_source_id: str | None = None,
        llm_source_id: str = "local_rules",
        entry_point: str = "continue",
        requested_minutes: int | None = None,
        guide_mode: str | None = None,
        display_name: str | None = None,
    ) -> AgentSessionStartResponse:
        profile = self.study_service.get_or_create_profile(user_id, display_name)
        pattern_summary = self.study_service.summarize_patterns(user_id)
        reference = reference or self._recommend_reference(entry_point, pattern_summary)
        resolved_text_source = (
            text_source_id or profile.preferences.preferred_translation_source_id or self.text_service.default_source
        )
        resolved_commentary_source = commentary_source_id or self.default_commentary_source
        resolved_mode = guide_mode or profile.preferences.preferred_guide_mode
        resolved_minutes = requested_minutes or pattern_summary.recommended_session_minutes

        passage = self.text_service.get_passage(reference, resolved_text_source)
        commentary_provider = self.commentary_registry.get(resolved_commentary_source)
        commentary = commentary_provider.get_commentary(reference)
        questions = self._generate_questions(pattern_summary, resolved_mode, entry_point)
        plan = self._generate_plan(resolved_minutes, passage.text, resolved_mode)

        prompt = (
            f"User pattern summary: {pattern_summary.model_dump_json()}\n"
            f"Passage: {passage.text}\n"
            f"Guide mode: {resolved_mode}\n"
            f"Entry point: {entry_point}"
        )
        guidance = self.llm_registry.get(llm_source_id).generate_guidance(prompt)
        latest_message = self._build_start_message(
            display_name=profile.display_name,
            reference=reference,
            requested_minutes=resolved_minutes,
            entry_point=entry_point,
            guidance=guidance,
        )

        session = StudySession(
            session_id=str(uuid4()),
            user_id=user_id,
            entry_point=entry_point,
            guide_mode=resolved_mode,
            requested_minutes=resolved_minutes,
            text_source_id=resolved_text_source,
            commentary_source_id=resolved_commentary_source,
            llm_source_id=llm_source_id,
            reference=reference,
            questions=questions,
            plan=plan,
            latest_message=latest_message,
        )
        session = self.study_service.create_session(session)
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="session_started",
                reference=reference,
                difficulty=pattern_summary.preferred_difficulty,
                engagement_score=3,
                notes=entry_point,
            )
        )
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="passage_viewed",
                reference=reference,
                difficulty=pattern_summary.preferred_difficulty,
                engagement_score=3,
                notes=resolved_text_source,
            )
        )
        return AgentSessionStartResponse(
            session=session,
            passage=passage,
            commentary=commentary,
            pattern_summary=pattern_summary,
            current_question=questions[0] if questions else None,
        )

    def respond_to_session(
        self,
        session_id: str,
        user_id: str,
        response_text: str,
        engagement_score: int = 3,
    ) -> AgentSessionTurnResponse:
        session = self.study_service.get_session(session_id)
        if session.user_id != user_id:
            raise KeyError(f"Session '{session_id}' does not belong to user '{user_id}'.")
        if session.status != "active":
            raise ValueError(f"Session '{session_id}' is already completed.")
        if session.current_question_index >= len(session.questions):
            raise ValueError("No questions remain in this session. Complete the session instead.")

        current_question = session.questions[session.current_question_index]
        response = SessionResponse(
            session_id=session.session_id,
            user_id=user_id,
            question_index=session.current_question_index,
            question=current_question.question,
            question_type=current_question.type,
            response_text=response_text,
        )
        self.study_service.add_session_response(response)
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="question_answered",
                reference=session.reference,
                difficulty=current_question.difficulty,
                engagement_score=engagement_score,
                notes=response_text[:280],
            )
        )

        next_index = session.current_question_index + 1
        next_question = session.questions[next_index] if next_index < len(session.questions) else None
        reply_message = self._build_follow_up_message(session.guide_mode, current_question.question, response_text, next_question)
        updated_session = session.model_copy(
            update={
                "current_question_index": next_index,
                "latest_message": reply_message,
            }
        )
        updated_session = self.study_service.save_session(updated_session)
        return AgentSessionTurnResponse(
            session=updated_session,
            reply_message=reply_message,
            next_question=next_question,
            remaining_questions=max(0, len(updated_session.questions) - updated_session.current_question_index),
        )

    def complete_session(
        self,
        session_id: str,
        user_id: str,
        summary_notes: str | None = None,
        action_item_title: str | None = None,
        action_item_detail: str | None = None,
        engagement_score: int = 4,
    ) -> AgentSessionCompleteResponse:
        session = self.study_service.get_session(session_id)
        if session.user_id != user_id:
            raise KeyError(f"Session '{session_id}' does not belong to user '{user_id}'.")
        if session.status == "completed":
            action_item = self.study_service.list_action_items(user_id)[0]
            return AgentSessionCompleteResponse(
                session=session,
                action_item=action_item,
                engagement=self.study_service.get_engagement_summary(user_id),
            )

        responses = self.study_service.list_session_responses(session_id)
        action_item = self._create_action_item(
            session=session,
            responses=responses,
            title=action_item_title,
            detail=action_item_detail,
        )
        created_action_item = self.study_service.create_action_item(action_item)

        completed_session = session.model_copy(
            update={
                "status": "completed",
                "completed_at": datetime.now(UTC),
                "latest_message": (
                    "Session complete. Keep the passage with you today and follow through on the action item before your next study."
                ),
                "action_item_id": created_action_item.action_item_id,
            }
        )
        completed_session = self.study_service.save_session(completed_session)
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="session_completed",
                reference=session.reference,
                difficulty=self.study_service.summarize_patterns(user_id).preferred_difficulty,
                engagement_score=engagement_score,
                notes=summary_notes,
            )
        )
        if summary_notes:
            self.study_service.record_event(
                StudyEvent(
                    user_id=user_id,
                    event_type="reflection_saved",
                    reference=session.reference,
                    difficulty=self.study_service.summarize_patterns(user_id).preferred_difficulty,
                    engagement_score=engagement_score,
                    notes=summary_notes,
                )
            )
        return AgentSessionCompleteResponse(
            session=completed_session,
            action_item=created_action_item,
            engagement=self.study_service.get_engagement_summary(user_id),
        )

    def _recommend_reference(self, entry_point: str, pattern_summary: StudyPatternSummary) -> PassageReference:
        if pattern_summary.recent_topics:
            recent = pattern_summary.recent_topics[-1]
            if recent.startswith("Psalm 23"):
                return PassageReference(book="Psalm", chapter=23, start_verse=1, end_verse=3)
            if recent.startswith("John 3"):
                return PassageReference(book="John", chapter=3, start_verse=16, end_verse=17)
        if entry_point in {"encouragement", "restart", "help me restart after missing a few days"}:
            return PassageReference(book="Psalm", chapter=23, start_verse=1, end_verse=3)
        return PassageReference(book="John", chapter=3, start_verse=16, end_verse=17)

    def _generate_questions(
        self,
        pattern_summary: StudyPatternSummary,
        guide_mode: str,
        entry_point: str,
    ) -> list[StudyQuestion]:
        difficulty = pattern_summary.preferred_difficulty
        closing_question = "What is one practical response you can make today based on this reading?"
        if guide_mode == "challenger":
            closing_question = "What comfortable assumption does this passage confront in your life right now?"
        elif guide_mode == "peer":
            closing_question = "What part of this passage feels most personal to you today?"
        elif guide_mode == "coach":
            closing_question = "What is one clear next step you will follow through on before your next session?"

        opener = "What repeated words or themes stand out in this passage?"
        if entry_point in {"encouragement", "I need encouragement"}:
            opener = "What in this passage meets you where you are emotionally today?"

        return [
            StudyQuestion(question=opener, type="observation", difficulty=difficulty),
            StudyQuestion(
                question="What does this passage reveal about God's character or intentions?",
                type="interpretation",
                difficulty=difficulty,
            ),
            StudyQuestion(question=closing_question, type="application", difficulty=difficulty),
        ]

    def _generate_plan(self, requested_minutes: int, passage_text: str, guide_mode: str) -> list[StudyPlanStep]:
        read_minutes = 5 if requested_minutes >= 15 else 3
        response_minutes = max(5, requested_minutes - (read_minutes + 5))
        closing_instruction = "Close by naming one concrete response for the next 24 hours."
        if guide_mode == "challenger":
            closing_instruction = "Close by naming one belief or habit this passage is pressing you to revisit."
        return [
            StudyPlanStep(
                title="Read Slowly",
                instruction=f"Read the selected text twice. Start with this excerpt: {passage_text[:180]}",
                estimated_minutes=read_minutes,
            ),
            StudyPlanStep(
                title="Reflect",
                instruction="Answer the guide's questions with honest, specific responses.",
                estimated_minutes=response_minutes,
            ),
            StudyPlanStep(
                title="Respond",
                instruction=closing_instruction,
                estimated_minutes=5,
            ),
        ]

    def _build_start_message(
        self,
        display_name: str | None,
        reference: PassageReference,
        requested_minutes: int,
        entry_point: str,
        guidance: str,
    ) -> str:
        greeting = f"Welcome back, {display_name}." if display_name else "Welcome back."
        return (
            f"{greeting} We'll spend about {requested_minutes} minutes in {reference.book} "
            f"{reference.chapter}:{reference.start_verse}"
            f"{'-' + str(reference.end_verse) if reference.end_verse else ''}. "
            f"This session starts from '{entry_point}'. {guidance}"
        )

    def _build_follow_up_message(
        self,
        guide_mode: str,
        question: str,
        response_text: str,
        next_question: StudyQuestion | None,
    ) -> str:
        depth_note = "Stay with that a little longer and keep it concrete." if len(response_text.strip()) < 80 else "That is a thoughtful response."
        if guide_mode == "challenger":
            depth_note = "Good. Do not settle for the easy answer here." if len(response_text.strip()) < 80 else "Good. Keep testing your assumptions against the text."
        elif guide_mode == "peer":
            depth_note = "Thanks for naming that honestly." if len(response_text.strip()) >= 40 else "That is a good start. Say a little more about what you mean."
        elif guide_mode == "coach":
            depth_note = "Strong. Let's make sure this turns into follow-through."
        if next_question is None:
            return f"{depth_note} You've worked through the main questions for this session. Complete the session to receive your action step."
        return f"{depth_note} Next question: {next_question.question}"

    def _create_action_item(
        self,
        session: StudySession,
        responses: list[SessionResponse],
        title: str | None,
        detail: str | None,
    ) -> ActionItem:
        last_response = responses[-1].response_text if responses else None
        generated_title = title or f"Live out {session.reference.book} {session.reference.chapter} today"
        generated_detail = detail or self._action_detail_from_response(session.reference, last_response)
        return ActionItem(
            action_item_id=str(uuid4()),
            user_id=session.user_id,
            session_id=session.session_id,
            title=generated_title,
            detail=generated_detail,
        )

    def _action_detail_from_response(self, reference: PassageReference, response_text: str | None) -> str:
        if response_text:
            snippet = response_text.strip().replace("\n", " ")[:180]
            return (
                f"Before your next session, act on what you wrote in response to {reference.book} {reference.chapter}. "
                f"Start here: {snippet}"
            )
        return (
            f"Before your next session, choose one concrete act of obedience, encouragement, or conversation that flows from "
            f"{reference.book} {reference.chapter}."
        )
