from __future__ import annotations

import http.client
import json
import socket
from abc import ABC, abstractmethod
from urllib import error, request

from emmaus.domain.models import StudyResponseEvaluation


class LLMProvider(ABC):
    source_id: str

    @abstractmethod
    def generate_guidance(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        raise NotImplementedError


class LLMProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider) -> None:
        self._providers[provider.source_id] = provider

    def get(self, source_id: str) -> LLMProvider:
        try:
            return self._providers[source_id]
        except KeyError as exc:
            raise KeyError(f"Unknown LLM provider '{source_id}'.") from exc


class NullLLMProvider(LLMProvider):
    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    def generate_guidance(self, prompt: str) -> str:
        if "Return JSON only" in prompt:
            return ""
        return "Stay close to the passage, answer honestly, and finish with one practical next step you can carry into today."

    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        return heuristic_response_evaluation(question_type=question_type, response_text=response_text)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        source_id: str,
        base_url: str,
        model: str,
        request_timeout_seconds: float = 20.0,
    ) -> None:
        self.source_id = source_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_timeout_seconds = request_timeout_seconds

    @staticmethod
    def is_available(base_url: str, timeout_seconds: float = 0.25) -> bool:
        tags_url = f"{base_url.rstrip('/')}/api/tags"
        try:
            with request.urlopen(tags_url, timeout=timeout_seconds) as response:
                return getattr(response, "status", 200) == 200
        except (error.URLError, TimeoutError, socket.timeout, http.client.HTTPException, ValueError):
            return False

    def generate_guidance(self, prompt: str) -> str:
        if "Return JSON only" in prompt:
            return ""
        body = self._post_generate(prompt)
        if body is None:
            return self._fallback_guidance(prompt)

        try:
            outer = json.loads(body)
            raw_response = str(outer.get("response", "")).strip()
            return raw_response or self._fallback_guidance(prompt)
        except (json.JSONDecodeError, TypeError, ValueError):
            return self._fallback_guidance(prompt)

    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        fallback = heuristic_response_evaluation(question_type=question_type, response_text=response_text)
        prompt = self._response_evaluation_prompt(
            passage_reference=passage_reference,
            passage_text=passage_text,
            question=question,
            question_type=question_type,
            response_text=response_text,
        )
        body = self._post_generate(prompt)
        if body is None:
            return fallback

        try:
            outer = json.loads(body)
            raw_response = str(outer.get("response", "")).strip()
            payload = json.loads(extract_json_object(raw_response))
        except (json.JSONDecodeError, ValueError, TypeError):
            return fallback

        try:
            return StudyResponseEvaluation(
                question_type=question_type,
                comprehension_score=clamp_score(payload.get("comprehension_score", fallback.comprehension_score)),
                application_score=clamp_score(payload.get("application_score", fallback.application_score)),
                clarity_score=clamp_score(payload.get("clarity_score", fallback.clarity_score)),
                recommended_focus=normalize_focus(payload.get("recommended_focus"), fallback.recommended_focus),
                encouragement=str(payload.get("encouragement") or fallback.encouragement).strip(),
                observed_patterns=normalize_patterns(payload.get("observed_patterns"), fallback.observed_patterns),
            )
        except (TypeError, ValueError):
            return fallback

    def _post_generate(self, prompt: str) -> str | None:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.request_timeout_seconds) as response:
                return response.read().decode("utf-8")
        except (error.URLError, TimeoutError, socket.timeout):
            return None

    def _response_evaluation_prompt(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> str:
        return (
            "You are Emmaus, a Christ-centered Bible study evaluator. "
            "Assess how well the user understood and applied the passage. "
            "Return JSON only with these keys: comprehension_score, application_score, clarity_score, "
            "recommended_focus, encouragement, observed_patterns. "
            "Scores must be decimals between 0 and 1. recommended_focus must be one of "
            "comprehension, application, consistency, growth. encouragement must be one short pastoral sentence. "
            "observed_patterns must be an array of 1 to 3 short strings. "
            "Prefer comprehension when the answer is vague or disconnected from the text. "
            "Prefer application when the answer is meaningful but not concrete.\n\n"
            f"Passage reference: {passage_reference}\n"
            f"Passage text: {passage_text}\n"
            f"Question type: {question_type}\n"
            f"Question: {question}\n"
            f"User response: {response_text}\n"
        )

    def _fallback_guidance(self, prompt: str) -> str:
        return (
            f"Ollama model '{self.model}' is unavailable, so Emmaus is falling back to local rule-based guidance for this session."
        )


def clamp_score(value: object) -> float:
    return round(max(0.0, min(1.0, float(value))), 2)


def normalize_focus(value: object, default: str) -> str:
    if isinstance(value, str) and value in {"comprehension", "application", "consistency", "growth"}:
        return value
    return default


def normalize_patterns(value: object, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        patterns = [str(item).strip() for item in value if str(item).strip()]
        if patterns:
            return patterns[:3]
    return fallback[:3]


def extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")
    return text[start : end + 1]


def heuristic_response_evaluation(question_type: str, response_text: str) -> StudyResponseEvaluation:
    normalized = response_text.strip()
    lowered = normalized.lower()
    words = [part for part in lowered.replace("\n", " ").split(" ") if part]
    word_count = len(words)

    comprehension = 0.25
    application = 0.2
    clarity = 0.25
    patterns: list[str] = []

    if word_count >= 18:
        clarity += 0.35
    elif word_count >= 9:
        clarity += 0.22
    elif word_count >= 5:
        clarity += 0.1
    else:
        patterns.append("The response is very brief and could be more specific.")

    if any(marker in lowered for marker in ["because", "shows", "means", "reveals", "therefore", "so that", "this passage"]):
        comprehension += 0.32
    if any(marker in lowered for marker in ["god", "jesus", "christ", "love", "grace", "mercy", "truth", "hope", "faith", "obedience"]):
        comprehension += 0.18

    if question_type in {"observation", "interpretation", "reflection"} and comprehension < 0.55:
        patterns.append("The answer needs a clearer connection to what the passage is saying.")

    if question_type == "application":
        if any(marker in lowered for marker in ["i will", "today", "tonight", "this week", "tomorrow", "pray", "text", "call", "encourage", "forgive", "apologize", "serve", "share", "discuss"]):
            application += 0.5
        elif any(marker in lowered for marker in ["should", "need to", "want to"]):
            application += 0.28
            patterns.append("The direction is meaningful, but the next step could be more concrete.")
        else:
            patterns.append("The response could move from reflection to one concrete action.")
        comprehension += 0.08
    elif any(marker in lowered for marker in ["obey", "apply", "practice", "respond", "live this"]):
        application += 0.18

    if any(character in normalized for character in [".", ",", ";", ":"]):
        clarity += 0.08

    comprehension = clamp_score(comprehension)
    application = clamp_score(application)
    clarity = clamp_score(clarity)
    recommended_focus = choose_focus(question_type, comprehension, application, clarity)
    encouragement = build_encouragement(recommended_focus, comprehension, application, clarity)

    if not patterns and recommended_focus == "growth":
        patterns.append("The response is specific enough to support a deeper follow-up next session.")

    return StudyResponseEvaluation(
        question_type=question_type,
        comprehension_score=comprehension,
        application_score=application,
        clarity_score=clarity,
        recommended_focus=recommended_focus,
        encouragement=encouragement,
        observed_patterns=patterns[:3],
    )


def choose_focus(question_type: str, comprehension: float, application: float, clarity: float) -> str:
    if question_type in {"observation", "interpretation", "reflection"} and min(comprehension, clarity) < 0.55:
        return "comprehension"
    if question_type == "application" and min(application, clarity) < 0.65:
        return "application"
    if comprehension >= 0.75 and application >= 0.7 and clarity >= 0.7:
        return "growth"
    if question_type == "application":
        return "application" if application < 0.78 else "growth"
    return "growth"


def build_encouragement(recommended_focus: str, comprehension: float, application: float, clarity: float) -> str:
    if recommended_focus == "comprehension":
        return "You're engaging honestly; stay close to the text and name what it actually says before moving on."
    if recommended_focus == "application":
        return "That's a meaningful direction; now turn it into one specific step you can actually follow through on."
    if comprehension >= 0.8 and application >= 0.75 and clarity >= 0.75:
        return "That response is clear and grounded, so you're ready for a deeper challenge."
    return "That's a solid response; keep building on it with a little more specificity and follow-through."

