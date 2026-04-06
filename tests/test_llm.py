import importlib
import json
from urllib import error

from emmaus.providers.llm import NullLLMProvider, OllamaProvider


class DummyHTTPResponse:
    def __init__(self, body: str, status: int = 200) -> None:
        self.body = body.encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False



def test_null_provider_scores_brief_application_response_as_application_gap():
    provider = NullLLMProvider(source_id="local_rules")

    evaluation = provider.evaluate_response(
        passage_reference="James 1:22-25",
        passage_text="Be doers of the word, and not hearers only.",
        question="What will you do today in response to this passage?",
        question_type="application",
        response_text="I should do better.",
    )

    assert evaluation.recommended_focus == "application"
    assert evaluation.application_score < 0.65
    assert "concrete" in " ".join(evaluation.observed_patterns).lower()



def test_ollama_provider_parses_structured_response_evaluation(monkeypatch):
    provider = OllamaProvider(
        source_id="local_rules",
        base_url="http://127.0.0.1:11434",
        model="phi3.5",
        request_timeout_seconds=0.1,
    )

    def fake_urlopen(*args, **kwargs):
        return DummyHTTPResponse(
            json.dumps(
                {
                    "response": json.dumps(
                        {
                            "comprehension_score": 0.82,
                            "application_score": 0.61,
                            "clarity_score": 0.77,
                            "recommended_focus": "application",
                            "encouragement": "That's thoughtful; now make the next step concrete.",
                            "observed_patterns": ["The response understands the passage but needs a clearer next step."],
                        }
                    )
                }
            )
        )

    monkeypatch.setattr("emmaus.providers.llm.request.urlopen", fake_urlopen)
    evaluation = provider.evaluate_response(
        passage_reference="Luke 24:13-17",
        passage_text="And Jesus himself drew near and went with them.",
        question="What does this passage reveal about Christ?",
        question_type="interpretation",
        response_text="Jesus moves toward discouraged disciples and helps them understand.",
    )

    assert evaluation.comprehension_score == 0.82
    assert evaluation.application_score == 0.61
    assert evaluation.recommended_focus == "application"
    assert evaluation.encouragement.startswith("That's thoughtful")



def test_ollama_provider_falls_back_when_request_fails(monkeypatch):
    provider = OllamaProvider(
        source_id="local_rules",
        base_url="http://127.0.0.1:11434",
        model="phi3.5",
        request_timeout_seconds=0.1,
    )

    def raise_url_error(*args, **kwargs):
        raise error.URLError("offline")

    monkeypatch.setattr("emmaus.providers.llm.request.urlopen", raise_url_error)
    guidance = provider.generate_guidance("Guide this study session.")
    evaluation = provider.evaluate_response(
        passage_reference="John 3:16-17",
        passage_text="For God so loved the world.",
        question="What stands out in this passage?",
        question_type="observation",
        response_text="God loves people.",
    )
    assert "phi3.5" in guidance
    assert "falling back" in guidance
    assert evaluation.comprehension_score >= 0
    assert evaluation.encouragement



def test_build_container_uses_null_provider_when_ollama_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("EMMAUS_DATABASE_PATH", str(tmp_path / "emmaus.sqlite3"))
    monkeypatch.setattr(OllamaProvider, "is_available", staticmethod(lambda base_url, timeout_seconds=0.25: False))

    import emmaus.core.bootstrap as bootstrap_module

    importlib.reload(bootstrap_module)
    container = bootstrap_module.build_container()
    assert isinstance(container.llm_registry.get("local_rules"), NullLLMProvider)



def test_build_container_uses_ollama_provider_when_available(tmp_path, monkeypatch):
    monkeypatch.setenv("EMMAUS_DATABASE_PATH", str(tmp_path / "emmaus.sqlite3"))
    monkeypatch.setenv("EMMAUS_OLLAMA_MODEL", "phi3.5")
    monkeypatch.setattr(OllamaProvider, "is_available", staticmethod(lambda base_url, timeout_seconds=0.25: True))

    import emmaus.core.bootstrap as bootstrap_module

    importlib.reload(bootstrap_module)
    container = bootstrap_module.build_container()
    provider = container.llm_registry.get("local_rules")
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "phi3.5"
