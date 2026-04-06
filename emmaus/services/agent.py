from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from uuid import uuid4

from emmaus.domain.models import (
    ActionItem,
    AgentSessionCompleteResponse,
    AgentSessionStartResponse,
    AgentSessionTurnResponse,
    AgentStudyResponse,
    PassageReference,
    PassageText,
    SessionResponse,
    SpiritualMemoryEntry,
    StudyEvent,
    StudyPatternSummary,
    StudyPlanStep,
    StudyQuestion,
    StudyRecommendation,
    StudyResponseEvaluation,
    StudySession,
)
from emmaus.providers.commentary import CommentaryProviderRegistry
from emmaus.providers.llm import LLMProviderRegistry
from emmaus.services.personalization import PersonalizationService
from emmaus.services.study import StudyService
from emmaus.services.text import TextSourceService


class AdaptiveStudyAgent:
    def __init__(
        self,
        study_service: StudyService,
        personalization_service: PersonalizationService,
        text_service: TextSourceService,
        commentary_registry: CommentaryProviderRegistry,
        llm_registry: LLMProviderRegistry,
        default_commentary_source: str,
    ) -> None:
        self.study_service = study_service
        self.personalization_service = personalization_service
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

    def recommend_next_session(self, user_id: str) -> StudyRecommendation:
        self.study_service.get_or_create_profile(user_id)
        return self.personalization_service.build_recommendation(user_id)

    def resume_active_session(self, user_id: str) -> AgentSessionStartResponse | None:
        self.study_service.get_or_create_profile(user_id)
        session = self.study_service.get_active_session(user_id)
        if session is None:
            return None
        pattern_summary = self.study_service.summarize_patterns(user_id)
        recommendation = self.personalization_service.build_recommendation(user_id)
        return self._build_session_response(session, pattern_summary, recommendation)

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
        recommendation = self.personalization_service.build_recommendation(user_id)
        reference = reference or recommendation.recommended_reference
        resolved_text_source = (
            text_source_id or profile.preferences.preferred_translation_source_id or self.text_service.default_source
        )
        resolved_commentary_source = commentary_source_id or self.default_commentary_source
        resolved_mode = guide_mode or recommendation.recommended_guide_mode or profile.preferences.preferred_guide_mode
        resolved_minutes = requested_minutes or recommendation.recommended_minutes or pattern_summary.recommended_session_minutes
        resolved_entry_point = entry_point if entry_point != "continue" else recommendation.recommended_entry_point

        passage = self.text_service.get_passage(reference, resolved_text_source)
        questions = self._generate_questions(
            pattern_summary=pattern_summary,
            guide_mode=resolved_mode,
            entry_point=resolved_entry_point,
            recommendation=recommendation,
            passage=passage,
            llm_source_id=llm_source_id,
        )
        plan = self._generate_plan(resolved_minutes, passage.text, resolved_mode, recommendation)

        prompt = (
            f"User pattern summary: {pattern_summary.model_dump_json()}\n"
            f"Recommendation: {recommendation.model_dump_json()}\n"
            f"Passage: {passage.text}\n"
            f"Guide mode: {resolved_mode}\n"
            f"Entry point: {resolved_entry_point}"
        )
        guidance = self.llm_registry.get(llm_source_id).generate_guidance(prompt)
        latest_message = self._build_start_message(
            display_name=profile.display_name,
            reference=reference,
            requested_minutes=resolved_minutes,
            entry_point=resolved_entry_point,
            guidance=guidance,
            recommendation=recommendation,
        )

        session = StudySession(
            session_id=str(uuid4()),
            user_id=user_id,
            entry_point=resolved_entry_point,
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
                notes=resolved_entry_point,
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
        return self._build_session_response(session, pattern_summary, recommendation)

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

        passage = self.text_service.get_passage(session.reference, session.text_source_id)
        evaluation = self.llm_registry.get(session.llm_source_id).evaluate_response(
            passage_reference=self._format_reference(session.reference),
            passage_text=passage.text,
            question=current_question.question,
            question_type=current_question.type,
            response_text=response_text,
        )
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="question_answered",
                reference=session.reference,
                difficulty=current_question.difficulty,
                engagement_score=engagement_score,
                notes=self._event_note(response_text, evaluation),
            )
        )

        next_index = session.current_question_index + 1
        next_question = session.questions[next_index] if next_index < len(session.questions) else None
        reply_message = self._build_follow_up_message(session.guide_mode, evaluation, next_question)
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
            evaluation=evaluation,
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
        memory_entry = self._create_spiritual_memory(
            session=completed_session,
            responses=responses,
            summary_notes=summary_notes,
            action_item=created_action_item,
        )
        self.study_service.record_spiritual_memory(memory_entry)

        preferred_difficulty = self.study_service.summarize_patterns(user_id).preferred_difficulty
        self.study_service.record_event(
            StudyEvent(
                user_id=user_id,
                event_type="session_completed",
                reference=session.reference,
                difficulty=preferred_difficulty,
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
                    difficulty=preferred_difficulty,
                    engagement_score=engagement_score,
                    notes=summary_notes,
                )
            )
        return AgentSessionCompleteResponse(
            session=completed_session,
            action_item=created_action_item,
            engagement=self.study_service.get_engagement_summary(user_id),
        )

    def _build_session_response(
        self,
        session: StudySession,
        pattern_summary: StudyPatternSummary,
        recommendation: StudyRecommendation,
    ) -> AgentSessionStartResponse:
        passage = self.text_service.get_passage(session.reference, session.text_source_id)
        commentary_source = session.commentary_source_id or self.default_commentary_source
        commentary_provider = self.commentary_registry.get(commentary_source)
        commentary = commentary_provider.get_commentary(session.reference)
        current_question = session.questions[session.current_question_index] if session.current_question_index < len(session.questions) else None
        return AgentSessionStartResponse(
            session=session,
            passage=passage,
            commentary=commentary,
            pattern_summary=pattern_summary,
            recommendation=recommendation,
            current_question=current_question,
        )

    def _generate_questions(
        self,
        pattern_summary: StudyPatternSummary,
        guide_mode: str,
        entry_point: str,
        recommendation: StudyRecommendation,
        passage: PassageText,
        llm_source_id: str,
    ) -> list[StudyQuestion]:
        difficulty = pattern_summary.preferred_difficulty
        llm_questions = self._generate_llm_questions(
            passage=passage,
            guide_mode=guide_mode,
            entry_point=entry_point,
            recommendation=recommendation,
            difficulty=difficulty,
            llm_source_id=llm_source_id,
        )
        if llm_questions is not None:
            return llm_questions

        anchor_phrase = self._extract_anchor_phrase(passage.text)
        contrast_phrase = self._extract_contrast_phrase(passage.text)
        primary_theme = self._primary_theme_label(passage.text)

        if recommendation.focus_area == "comprehension":
            return [
                StudyQuestion(
                    question=f"Which phrase should you slow down and notice first in this passage? Start with '{anchor_phrase}'.",
                    type="observation",
                    difficulty=difficulty,
                ),
                StudyQuestion(
                    question=self._interpretation_question(contrast_phrase, primary_theme),
                    type="interpretation",
                    difficulty=difficulty,
                ),
                StudyQuestion(
                    question=f"What part of '{anchor_phrase}' still feels unclear or worth a second look before you move on?",
                    type="reflection",
                    difficulty=difficulty,
                ),
            ]

        opener = self._observation_question(entry_point, recommendation.focus_area, anchor_phrase, primary_theme)
        closing_question = self._application_question(guide_mode, recommendation.focus_area, primary_theme)

        return [
            StudyQuestion(question=opener, type="observation", difficulty=difficulty),
            StudyQuestion(
                question=self._interpretation_question(contrast_phrase, primary_theme),
                type="interpretation",
                difficulty=difficulty,
            ),
            StudyQuestion(question=closing_question, type="application", difficulty=difficulty),
        ]

    def _generate_llm_questions(
        self,
        passage: PassageText,
        guide_mode: str,
        entry_point: str,
        recommendation: StudyRecommendation,
        difficulty: str,
        llm_source_id: str,
    ) -> list[StudyQuestion] | None:
        prompt = (
            "You are Emmaus, creating Bible study questions for a mobile-first session. "
            "Return JSON only as an array of exactly 3 objects with keys: question, type, difficulty. "
            "Types must be observation, interpretation, or application. "
            "Each question should be concise, passage-aware, and easy to answer on a phone. "
            "At least one question must quote or clearly echo a phrase from the passage.\n\n"
            f"Passage reference: {self._format_reference(passage.reference)}\n"
            f"Passage text: {passage.text}\n"
            f"Guide mode: {guide_mode}\n"
            f"Entry point: {entry_point}\n"
            f"Focus area: {recommendation.focus_area}\n"
            f"Difficulty: {difficulty}\n"
        )
        raw = self.llm_registry.get(llm_source_id).generate_guidance(prompt)
        try:
            payload = json.loads(self._extract_json_payload(raw))
        except (json.JSONDecodeError, ValueError, TypeError):
            return None
        if not isinstance(payload, list) or len(payload) != 3:
            return None

        questions: list[StudyQuestion] = []
        valid_types = {"observation", "interpretation", "application"}
        for item in payload:
            if not isinstance(item, dict):
                return None
            question = str(item.get("question", "")).strip()
            question_type = str(item.get("type", "")).strip()
            question_difficulty = str(item.get("difficulty") or difficulty).strip() or difficulty
            if not question or question_type not in valid_types:
                return None
            questions.append(
                StudyQuestion(
                    question=question,
                    type=question_type,
                    difficulty=question_difficulty if question_difficulty in {"gentle", "balanced", "challenging"} else difficulty,
                )
            )
        return questions

    def _observation_question(self, entry_point: str, focus_area: str, anchor_phrase: str, primary_theme: str) -> str:
        if entry_point in {"encouragement", "I need encouragement"}:
            return f"Which words in '{anchor_phrase}' meet you where you are emotionally today?"
        if focus_area == "application":
            return f"Which line in this passage is easiest to admire but hardest to live out? Start with '{anchor_phrase}'."
        if focus_area == "consistency":
            return f"Which part of '{anchor_phrase}' gives you a simple place to begin again today?"
        if focus_area == "growth":
            return f"What deeper tension or challenge stands out when you sit with '{anchor_phrase}'?"
        return f"Which words or repeated idea stand out first in this passage? Start with '{anchor_phrase}'."

    def _interpretation_question(self, contrast_phrase: str | None, primary_theme: str) -> str:
        if contrast_phrase:
            return f"How does the contrast '{contrast_phrase}' shape what this passage reveals about God and his intentions?"
        return f"What does this passage teach about {primary_theme}, and how do you see that in the text itself?"

    def _application_question(self, guide_mode: str, focus_area: str, primary_theme: str) -> str:
        if guide_mode == "challenger":
            return f"If this passage is really about {primary_theme}, what comfortable assumption in your life does it confront right now?"
        if guide_mode == "peer":
            return f"Where does this passage about {primary_theme} feel most personal to you today?"
        if guide_mode == "coach":
            return f"Because this passage centers on {primary_theme}, what is one clear next step you will follow through on before your next session?"
        if focus_area == "application":
            return f"Because this passage emphasizes {primary_theme}, what is one concrete response you can make in the next 24 hours?"
        return f"How should the truth about {primary_theme} change one real choice you make today?"

    def _extract_anchor_phrase(self, passage_text: str) -> str:
        cleaned = re.sub(r"\s+", " ", passage_text).strip()
        segments = [segment.strip(" .;:") for segment in re.split(r"[.;]", cleaned) if segment.strip()]
        if not segments:
            return "this passage"
        prioritized = sorted(segments, key=self._segment_priority, reverse=True)
        anchor = prioritized[0]
        return anchor[:90] + "..." if len(anchor) > 90 else anchor

    def _extract_contrast_phrase(self, passage_text: str) -> str | None:
        match = re.search(r"([^.;]*\bbut\b[^.;]*)", passage_text, flags=re.IGNORECASE)
        if not match:
            return None
        contrast = match.group(1).strip(" .;")
        return contrast[:110] + "..." if len(contrast) > 110 else contrast

    def _segment_priority(self, segment: str) -> tuple[int, int]:
        lower = segment.lower()
        score = 0
        for keyword in ["god", "jesus", "christ", "love", "saved", "condemn", "world", "shepherd", "restore", "righteousness", "grace", "mercy"]:
            if keyword in lower:
                score += 1
        return score, len(segment)

    def _primary_theme_label(self, passage_text: str) -> str:
        lower = passage_text.lower()
        if "love" in lower:
            return "God's love"
        if "saved" in lower or "salvation" in lower:
            return "God's saving purpose"
        if "condemn" in lower:
            return "mercy instead of condemnation"
        if "shepherd" in lower:
            return "the Lord's shepherding care"
        if "restore" in lower or "still waters" in lower:
            return "rest and restoration"
        return "God's character"

    def _extract_json_payload(self, value: str) -> str:
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            return text
        if text.startswith("{") and text.endswith("}"):
            return text
        match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text)
        if not match:
            raise ValueError("No JSON payload found.")
        return match.group(1)

    def _generate_plan(
        self,
        requested_minutes: int,
        passage_text: str,
        guide_mode: str,
        recommendation: StudyRecommendation,
    ) -> list[StudyPlanStep]:
        read_minutes = 5 if requested_minutes >= 15 else 3
        response_minutes = max(5, requested_minutes - (read_minutes + 5))
        focus_instruction = "Let the guide help you slow down and respond honestly."
        if recommendation.focus_area == "comprehension":
            focus_instruction = "Move slowly and focus on understanding what the passage is actually saying before jumping ahead."
        elif recommendation.focus_area == "application":
            focus_instruction = "Pay special attention to where the passage demands a real-life response."
        elif recommendation.focus_area == "consistency":
            focus_instruction = "Keep this session simple and completeable so it rebuilds momentum."
        elif recommendation.focus_area == "growth":
            focus_instruction = "Use this session to push beyond the obvious and explore a deeper challenge."

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
                title="Focus",
                instruction=focus_instruction,
                estimated_minutes=2,
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
        recommendation: StudyRecommendation,
    ) -> str:
        greeting = f"Welcome back, {display_name}." if display_name else "Welcome back."
        return (
            f"{greeting} We'll spend about {requested_minutes} minutes in {reference.book} "
            f"{reference.chapter}:{reference.start_verse}"
            f"{'-' + str(reference.end_verse) if reference.end_verse else ''}. "
            f"This session starts from '{entry_point}' and focuses on {recommendation.focus_area}. {guidance}"
        )

    def _build_follow_up_message(
        self,
        guide_mode: str,
        evaluation: StudyResponseEvaluation,
        next_question: StudyQuestion | None,
    ) -> str:
        guide_prefix = {
            "guide": "Stay close to the passage.",
            "peer": "You're naming this honestly.",
            "challenger": "Press a little deeper here.",
            "coach": "Let's turn this into follow-through.",
        }[guide_mode]
        focus_hint = {
            "comprehension": "Keep looking for what the text actually says before moving too quickly to application.",
            "application": "Name the next step in a way you can actually do today.",
            "consistency": "Keep the next step simple enough to finish.",
            "growth": "You're ready to press a little deeper on the next question.",
        }[evaluation.recommended_focus]
        if next_question is None:
            return (
                f"{evaluation.encouragement} {guide_prefix} {focus_hint} "
                "You've worked through the main questions for this session. Complete the session to receive your action step."
            )
        return f"{evaluation.encouragement} {guide_prefix} {focus_hint} Next question: {next_question.question}"

    def _create_action_item(
        self,
        session: StudySession,
        responses: list[SessionResponse],
        title: str | None,
        detail: str | None,
    ) -> ActionItem:
        passage = self.text_service.get_passage(session.reference, session.text_source_id)
        last_response = responses[-1].response_text if responses else None
        generated_title, generated_detail = self._generate_action_item_content(
            session=session,
            passage=passage,
            last_response=last_response,
        )
        return ActionItem(
            action_item_id=str(uuid4()),
            user_id=session.user_id,
            session_id=session.session_id,
            title=title or generated_title,
            detail=detail or generated_detail,
        )

    def _generate_action_item_content(
        self,
        session: StudySession,
        passage: PassageText,
        last_response: str | None,
    ) -> tuple[str, str]:
        prompt = (
            "You are Emmaus, creating a single practical Bible study action item for a mobile user. "
            "Return JSON only with keys title and detail. Title should be 4 to 8 words. "
            "Detail should be one short paragraph with one concrete, realistic next step in the next 24 hours. "
            "Keep it Christ-centered, specific, and tied to the passage.\n\n"
            f"Passage reference: {self._format_reference(session.reference)}\n"
            f"Passage text: {passage.text}\n"
            f"Guide mode: {session.guide_mode}\n"
            f"Last user response: {last_response or 'None'}\n"
        )
        raw = self.llm_registry.get(session.llm_source_id).generate_guidance(prompt)
        try:
            payload = json.loads(self._extract_json_payload(raw))
        except (json.JSONDecodeError, ValueError, TypeError):
            return self._fallback_action_item_content(session.reference, passage.text, last_response)

        if not isinstance(payload, dict):
            return self._fallback_action_item_content(session.reference, passage.text, last_response)

        title = str(payload.get("title", "")).strip()
        detail = str(payload.get("detail", "")).strip()
        if not title or not detail:
            return self._fallback_action_item_content(session.reference, passage.text, last_response)
        return title[:80], detail[:280]

    def _fallback_action_item_content(
        self,
        reference: PassageReference,
        passage_text: str,
        response_text: str | None,
    ) -> tuple[str, str]:
        primary_theme = self._primary_theme_label(passage_text)
        response_snippet = response_text.strip().replace("\n", " ")[:140] if response_text else None
        if response_snippet:
            if any(keyword in response_snippet.lower() for keyword in ["encourage", "text", "call", "friend", "someone"]):
                return (
                    f"Practice {primary_theme} today"[:80],
                    f"Before your next session, act on what you wrote from {reference.book} {reference.chapter}. Reach out to one person today and follow through on this step: {response_snippet}"[:280],
                )
            return (
                f"Respond to {primary_theme}"[:80],
                f"Before your next session, turn your reflection from {reference.book} {reference.chapter} into one concrete action in the next 24 hours. Start here: {response_snippet}"[:280],
            )
        return (
            f"Live out {primary_theme}"[:80],
            f"Before your next session, choose one concrete act of obedience, encouragement, or prayer that flows from {reference.book} {reference.chapter} and complete it in the next 24 hours."[:280],
        )

    def _create_spiritual_memory(
        self,
        session: StudySession,
        responses: list[SessionResponse],
        summary_notes: str | None,
        action_item: ActionItem,
    ) -> SpiritualMemoryEntry:
        passage = self.text_service.get_passage(session.reference, session.text_source_id)
        summary, recurring_themes, growth_areas, carry_forward_prompt = self._generate_spiritual_memory_content(
            session=session,
            passage=passage,
            responses=responses,
            summary_notes=summary_notes,
            action_item=action_item,
        )
        return SpiritualMemoryEntry(
            memory_id=str(uuid4()),
            user_id=session.user_id,
            session_id=session.session_id,
            reference=session.reference,
            summary=summary,
            recurring_themes=recurring_themes,
            growth_areas=growth_areas,
            carry_forward_prompt=carry_forward_prompt,
        )

    def _generate_spiritual_memory_content(
        self,
        session: StudySession,
        passage: PassageText,
        responses: list[SessionResponse],
        summary_notes: str | None,
        action_item: ActionItem,
    ) -> tuple[str, list[str], list[str], str]:
        response_snippets = [
            f"{response.question_type}: {response.response_text.strip().replace(chr(10), ' ')[:160]}"
            for response in responses
            if response.response_text.strip()
        ]
        prompt = (
            "You are Emmaus, creating a compact spiritual memory after a Bible study session. "
            "Return JSON only with keys summary, recurring_themes, growth_areas, carry_forward_prompt. "
            "summary should be one short paragraph in plain language. "
            "recurring_themes and growth_areas should each be arrays of 1 to 3 short phrases. "
            "carry_forward_prompt should be one concise sentence Emmaus can use to reconnect the user next time. "
            "Keep everything Christ-centered, grounded in the passage, and easy to display on mobile.\n\n"
            f"Passage reference: {self._format_reference(session.reference)}\n"
            f"Passage text: {passage.text}\n"
            f"Guide mode: {session.guide_mode}\n"
            f"Session summary notes: {summary_notes or 'None'}\n"
            f"Action item title: {action_item.title}\n"
            f"Action item detail: {action_item.detail}\n"
            f"User responses: {json.dumps(response_snippets)}\n"
        )
        raw = self.llm_registry.get(session.llm_source_id).generate_guidance(prompt)
        try:
            payload = json.loads(self._extract_json_payload(raw))
        except (json.JSONDecodeError, ValueError, TypeError):
            return self._fallback_spiritual_memory_content(session.reference, passage.text, responses, summary_notes, action_item)

        if not isinstance(payload, dict):
            return self._fallback_spiritual_memory_content(session.reference, passage.text, responses, summary_notes, action_item)

        summary = str(payload.get("summary", "")).strip()
        recurring_themes = self._normalize_short_list(payload.get("recurring_themes"))
        growth_areas = self._normalize_short_list(payload.get("growth_areas"))
        carry_forward_prompt = str(payload.get("carry_forward_prompt", "")).strip()
        if not summary or not recurring_themes or not growth_areas or not carry_forward_prompt:
            return self._fallback_spiritual_memory_content(session.reference, passage.text, responses, summary_notes, action_item)
        return summary[:320], recurring_themes[:3], growth_areas[:3], carry_forward_prompt[:180]

    def _fallback_spiritual_memory_content(
        self,
        reference: PassageReference,
        passage_text: str,
        responses: list[SessionResponse],
        summary_notes: str | None,
        action_item: ActionItem,
    ) -> tuple[str, list[str], list[str], str]:
        primary_theme = self._primary_theme_label(passage_text)
        last_response = responses[-1].response_text.strip().replace("\n", " ")[:160] if responses else ""
        summary_seed = summary_notes.strip() if summary_notes else last_response
        if summary_seed:
            summary = (
                f"In {reference.book} {reference.chapter}, Emmaus saw the user returning to {primary_theme} while reflecting on this response: {summary_seed}."
            )[:320]
        else:
            summary = (
                f"In {reference.book} {reference.chapter}, Emmaus saw the user engaging {primary_theme} and moving toward a concrete response."
            )[:320]

        recurring_themes = [primary_theme]
        if any("encour" in response.response_text.lower() for response in responses):
            recurring_themes.append("encouraging others")
        elif any("pray" in response.response_text.lower() for response in responses):
            recurring_themes.append("prayerful dependence")
        else:
            recurring_themes.append("responding to Scripture personally")

        growth_areas = []
        if any(response.question_type == "interpretation" for response in responses):
            growth_areas.append("slowing down to understand the passage")
        if any(response.question_type in {"application", "reflection"} for response in responses):
            growth_areas.append("turning insight into concrete follow-through")
        if not growth_areas:
            growth_areas.append("carrying Scripture into daily life")

        carry_forward_prompt = (
            f"Return to {primary_theme} and follow through on '{action_item.title}' before moving on to something new."
        )[:180]
        return summary, recurring_themes[:3], growth_areas[:3], carry_forward_prompt

    def _normalize_short_list(self, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            text = str(item).strip()
            if text and text not in seen:
                seen.add(text)
                normalized.append(text[:80])
        return normalized

    def _event_note(self, response_text: str, evaluation: StudyResponseEvaluation) -> str:
        snippet = response_text.strip().replace("\n", " ")[:140]
        return (
            f"{snippet} | focus={evaluation.recommended_focus} | "
            f"comp={evaluation.comprehension_score:.2f} app={evaluation.application_score:.2f} clarity={evaluation.clarity_score:.2f}"
        )

    def _format_reference(self, reference: PassageReference) -> str:
        ending = f"-{reference.end_verse}" if reference.end_verse else ""
        return f"{reference.book} {reference.chapter}:{reference.start_verse}{ending}"
