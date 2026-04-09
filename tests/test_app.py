import importlib
from collections import Counter
import json

from fastapi.testclient import TestClient

from emmaus.domain.models import StudyGapReport, StudyResponseEvaluation
from emmaus.providers.llm import LLMProvider
from emmaus.services.personalization import CURATED_PASSAGE_BANK


class WeakComprehensionProvider(LLMProvider):
    source_id = "local_rules"

    def generate_guidance(self, prompt: str) -> str:
        return "Let's walk through this passage slowly and carefully."

    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        if question_type == "application":
            return StudyResponseEvaluation(
                question_type=question_type,
                comprehension_score=0.72,
                application_score=0.82,
                clarity_score=0.76,
                recommended_focus="growth",
                encouragement="That's a practical response; keep it grounded in the passage.",
                observed_patterns=["The action step is concrete enough to build on."],
            )
        return StudyResponseEvaluation(
            question_type=question_type,
            comprehension_score=0.28,
            application_score=0.42,
            clarity_score=0.38,
            recommended_focus="comprehension",
            encouragement="Stay closer to the text and name what you see before moving on.",
            observed_patterns=["The answer needs a clearer connection to the passage itself."],
        )


class StrongResponseProvider(LLMProvider):
    source_id = "local_rules"

    def generate_guidance(self, prompt: str) -> str:
        return "This session is tuned to build from what you've already been learning."

    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        return StudyResponseEvaluation(
            question_type=question_type,
            comprehension_score=0.88,
            application_score=0.84,
            clarity_score=0.86,
            recommended_focus="growth",
            encouragement="That's a strong response; you're ready to go a little deeper.",
            observed_patterns=["The response is specific and grounded in the passage."],
        )



class CountingEvaluationProvider(LLMProvider):
    source_id = "local_rules"

    def __init__(self) -> None:
        self.evaluate_calls = 0

    def generate_guidance(self, prompt: str) -> str:
        return "Let's stay close to the passage and keep moving one clear step at a time."

    def evaluate_response(
        self,
        passage_reference: str,
        passage_text: str,
        question: str,
        question_type: str,
        response_text: str,
    ) -> StudyResponseEvaluation:
        self.evaluate_calls += 1
        return StudyResponseEvaluation(
            question_type=question_type,
            comprehension_score=0.74,
            application_score=0.71,
            clarity_score=0.73,
            recommended_focus="application",
            encouragement="Stay specific and keep your answer anchored in what the passage is calling for.",
            observed_patterns=["The response is moving in a healthy direction."],
        )



def build_client(tmp_path, monkeypatch):
    monkeypatch.setenv("EMMAUS_DATABASE_PATH", str(tmp_path / "emmaus.sqlite3"))
    import emmaus.main as main_module

    importlib.reload(main_module)
    return TestClient(main_module.app)



def test_healthcheck(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_frontend_shell_and_assets(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Start Today's Plan" in response.text
    assert "Demo Mode" in response.text
    assert "data-demo-scenario=\"comprehension_gap\"" in response.text
    assert "data-demo-scenario=\"scheduled_nudge\"" in response.text
    assert "translation-template-list" in response.text
    assert "source-preview-card" in response.text
    assert "source-library" in response.text
    assert "source-use-starter" in response.text
    assert "source-esv-form" in response.text
    assert "source-upload-form" in response.text
    assert "source-advanced-toggle" in response.text
    assert "onboarding-step-pill" in response.text
    assert "onboarding-flow" in response.text
    assert "memory-thread-card" in response.text
    assert "memory-thread-pill" in response.text
    assert "completion-summary-card" in response.text
    assert "completion-summary-pill" in response.text
    assert "follow-up-target-copy" in response.text
    assert "question-style-select" in response.text
    assert "guidance-tone-select" in response.text
    assert '<option value="America/New_York">Eastern Time (EST/EDT)</option>' in response.text
    assert "prayer-item-list" in response.text
    assert "prayer-form" in response.text
    assert "review-history-card" in response.text
    assert "review-summary-pill" in response.text
    assert "Look back with clarity" in response.text
    assert "Change Bible" in response.text
    assert "Your current Bible" in response.text
    assert "Default for new sessions" in response.text
    assert 'id="home-bible-current-name"' in response.text
    assert 'id="profile-bible-panel"' in response.text
    assert "nudge-plan-card" in response.text
    assert response.text.count('id="identity-form"') == 1
    assert response.text.count('id="mood-form"') == 1
    assert response.text.count('id="source-manager-copy"') == 1
    assert 'data-nav-target="profile"' in response.text
    assert 'data-nav-target="nudges"' not in response.text

    asset = client.get("/static/app.js")
    assert asset.status_code == 200
    assert "demoScenario" in asset.text
    assert "buildDemoScenarioData" in asset.text
    assert "comprehension_gap" in asset.text
    assert "setPreferredBibleSource" in asset.text
    assert "buildGeneratedSourceId" in asset.text
    assert "onConnectEsvSource" in asset.text
    assert "renderTranslationTemplates" in asset.text
    assert "renderSourcePreview" in asset.text
    assert "openBibleSettingsInProfile" in asset.text
    assert "resetViewportScroll" in asset.text
    assert "review-history-details" in asset.text
    assert "How this session will work" in asset.text
    assert "previewBibleSource" in asset.text
    assert "onTranslationTemplateClick" in asset.text
    assert "buildPassageMarkup" in asset.text
    assert "deriveOnboardingStep" in asset.text
    assert "renderMemorySummary" in asset.text
    assert "Keep building here:" in asset.text
    assert "Growth edge:" in asset.text
    assert "buildSessionContextCard" in asset.text
    assert "question-transition-copy" in response.text
    assert "buildSessionPrayerCard" in asset.text
    assert "bindActionFieldTabFill" in asset.text
    assert "buildPassageHelpsMarkup" in asset.text
    assert "buildCommentaryNotesMarkup" in asset.text
    assert "scripture-adjacent-note" in asset.text
    assert "commentary-handoff" in asset.text
    assert "scripture-adjacent-helps" in asset.text
    assert "commentary-details" in asset.text
    assert "Pray before you continue" in asset.text
    assert "Why this passage today" in asset.text
    assert "renderCompletionSummary" in asset.text
    assert "Carry this with you today" in asset.text
    assert "lastFollowThroughUpdate" in asset.text
    assert "buildNudgeThreadContext" in asset.text
    assert "Why Emmaus is reaching out" in asset.text
    assert "Build on what already landed" in asset.text
    assert "startGuidedSession" in asset.text
    assert "source-use-starter" in response.text
    assert "source-upload-file" in asset.text
    assert "followUpOutcomeSelect" in asset.text
    assert "delivery_status" in asset.text



def test_text_source_templates_expose_translation_first_setup_options(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/v1/sources/text/templates")
    assert response.status_code == 200
    payload = response.json()
    items = payload["items"]
    assert any(item["template_id"] == "starter" for item in items)
    assert any(item["template_id"] == "esv" and item["setup_mode"] == "esv_api" for item in items)
    assert any(item["template_id"] == "kjv" and item["setup_mode"] == "upload" for item in items)
    assert any(item["template_id"] == "licensed_other" and item["setup_mode"] == "generic_api" for item in items)


def test_commentary_sources_include_jfb(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/v1/commentary/sources")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["source_id"] == "jfb_commentary" for item in items)



def test_uploaded_text_source_can_be_registered_and_used(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    uploaded_source = client.post(
        "/v1/sources/text/upload",
        json={
            "source_id": "uploaded_demo",
            "name": "Uploaded Demo Bible",
            "filename": "uploaded_demo.json",
            "file_content": json.dumps(
                {
                    "name": "Uploaded Demo Bible",
                    "copyright": "Public Domain",
                    "books": {
                        "John": {
                            "1": {
                                "1": "In the beginning was the Word.",
                                "2": "The same was in the beginning with God.",
                            }
                        }
                    },
                }
            ),
            "license_name": "Public Domain",
        },
    )
    assert uploaded_source.status_code == 201
    descriptor = uploaded_source.json()
    assert descriptor["source_id"] == "uploaded_demo"
    assert descriptor["provider_type"] == "local_file"

    passage = client.post(
        "/v1/texts/passage",
        json={
            "source_id": "uploaded_demo",
            "book": "John",
            "chapter": 1,
            "start_verse": 1,
            "end_verse": 2,
        },
    )
    assert passage.status_code == 200
    payload = passage.json()
    assert payload["source_id"] == "uploaded_demo"
    assert "In the beginning was the Word." in payload["text"]



def test_esv_text_source_can_be_registered_and_used(tmp_path, monkeypatch):
    def fake_urlopen(req, timeout=15):
        class DummyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({
                    "canonical": "John 3:16-17",
                    "passages": ["For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life."],
                }).encode("utf-8")

        return DummyResponse()

    monkeypatch.setattr("emmaus.providers.text.request.urlopen", fake_urlopen)
    client = build_client(tmp_path, monkeypatch)

    registered = client.post(
        "/v1/sources/text/esv",
        json={"api_key": "secret-esv-key"},
    )
    assert registered.status_code == 201
    descriptor = registered.json()
    assert descriptor["source_id"] == "esv"
    assert descriptor["metadata"]["vendor"] == "esv"

    passage = client.post(
        "/v1/texts/passage",
        json={
            "source_id": "esv",
            "book": "John",
            "chapter": 3,
            "start_verse": 16,
            "end_verse": 17,
        },
    )
    assert passage.status_code == 200
    payload = passage.json()
    assert payload["source_id"] == "esv"
    assert payload["translation_name"] == "ESV"
    assert "For God so loved the world" in payload["text"]
    assert "Crossway" in payload["copyright_notice"]



def test_esv_session_includes_passage_helps(tmp_path, monkeypatch):
    def fake_text_urlopen(req, timeout=15):
        class DummyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                url = req.full_url if hasattr(req, "full_url") else str(req)
                if "passage/html" in url:
                    return json.dumps({
                        "canonical": "John 3:16-17",
                        "passages": [
                            "<h2>The New Birth</h2><p>For God so loved the world<sup class=\"footnote\">a</sup>.</p><div class=\"footnotes\"><p>a Or This is a clarifying footnote.</p></div><div class=\"crossrefs\"><p>See Rom. 5:8; 1 John 4:9.</p></div>"
                        ],
                    }).encode("utf-8")
                return json.dumps({
                    "canonical": "John 3:16-17",
                    "passages": ["For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life."],
                }).encode("utf-8")

        return DummyResponse()

    monkeypatch.setenv("EMMAUS_ESV_API_KEY", "configured-esv-key")
    monkeypatch.setattr("emmaus.providers.text.request.urlopen", fake_text_urlopen)
    monkeypatch.setattr("emmaus.providers.commentary.request.urlopen", fake_text_urlopen)
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "esv",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    payload = start.json()
    assert payload["session"]["commentary_source_id"] == "jfb_commentary"
    assert any(note["source_id"] == "jfb_commentary" for note in payload["commentary"])
    assert any(note["metadata"].get("kind") == "commentary" for note in payload["commentary"])
    assert any(note["metadata"].get("section") == "headings" for note in payload["commentary"])
    assert any(note["metadata"].get("section") == "crossrefs" for note in payload["commentary"])
    assert payload["commentary"]
    assert any(note["metadata"].get("kind") == "passage_helps" for note in payload["commentary"])
    combined = " ".join(f"{note['title']} {note['body']}" for note in payload["commentary"])
    assert "footnote" in combined.lower() or "cross-reference" in combined.lower() or "section headings" in combined.lower()
    assert "heart of god" in combined.lower() or "sent so that those who believe might live" in combined.lower()
def test_esv_session_omits_plain_text_passage_help_fallback(tmp_path, monkeypatch):
    def fake_text_urlopen(req, timeout=15):
        class DummyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                url = req.full_url if hasattr(req, "full_url") else str(req)
                if "passage/html" in url:
                    return json.dumps({
                        "canonical": "John 3:16-17",
                        "passages": [
                            "<p>For God so loved the world, that he gave his only Son.</p>"
                        ],
                    }).encode("utf-8")
                return json.dumps({
                    "canonical": "John 3:16-17",
                    "passages": ["For God so loved the world, that he gave his only Son."],
                }).encode("utf-8")

        return DummyResponse()

    monkeypatch.setenv("EMMAUS_ESV_API_KEY", "configured-esv-key")
    monkeypatch.setattr("emmaus.providers.text.request.urlopen", fake_text_urlopen)
    monkeypatch.setattr("emmaus.providers.commentary.request.urlopen", fake_text_urlopen)
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "esv",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    payload = start.json()
    assert any(note["metadata"].get("kind") == "commentary" for note in payload["commentary"])
    assert not any(note["metadata"].get("kind") == "passage_helps" for note in payload["commentary"])


def test_existing_esv_session_with_placeholder_commentary_uses_jfb(tmp_path, monkeypatch):
    def fake_text_urlopen(req, timeout=15):
        class DummyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                url = req.full_url if hasattr(req, "full_url") else str(req)
                if "passage/html" in url:
                    return json.dumps({
                        "canonical": "John 3:16-17",
                        "passages": [
                            '<h2>The New Birth</h2><p>For God so loved the world.</p><div class="crossrefs"><p>See Rom. 5:8.</p></div>'
                        ],
                    }).encode("utf-8")
                return json.dumps({
                    "canonical": "John 3:16-17",
                    "passages": ["For God so loved the world, that he gave his only Son."],
                }).encode("utf-8")

        return DummyResponse()

    monkeypatch.setenv("EMMAUS_ESV_API_KEY", "configured-esv-key")
    monkeypatch.setattr("emmaus.providers.text.request.urlopen", fake_text_urlopen)
    monkeypatch.setattr("emmaus.providers.commentary.request.urlopen", fake_text_urlopen)
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "esv",
            "commentary_source_id": "notes_placeholder",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    payload = start.json()
    assert payload["session"]["commentary_source_id"] == "notes_placeholder"
    assert any(note["source_id"] == "jfb_commentary" for note in payload["commentary"])
    assert any(note["metadata"].get("kind") == "passage_helps" for note in payload["commentary"])


def test_configured_esv_becomes_effective_default_source(tmp_path, monkeypatch):
    def fake_urlopen(req, timeout=15):
        class DummyResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({
                    "canonical": "Psalm 23:1-3",
                    "passages": ["The Lord is my shepherd; I shall not want. He makes me lie down in green pastures."],
                }).encode("utf-8")

        return DummyResponse()

    monkeypatch.setenv("EMMAUS_ESV_API_KEY", "configured-esv-key")
    monkeypatch.setattr("emmaus.providers.text.request.urlopen", fake_urlopen)
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    payload = start.json()
    assert payload["session"]["text_source_id"] == "esv"
    assert payload["passage"]["source_id"] == "esv"


def test_update_preferences_and_profile(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    update_response = client.patch(
        "/v1/users/demo-user/preferences",
        json={
            "display_name": "Brian",
            "preferred_session_minutes": 15,
            "preferred_guide_mode": "coach",
            "preferred_difficulty": "gentle",
            "preferred_translation_source_id": "sample_local",
            "nudge_intensity": "direct",
            "timezone": "America/New_York",
            "preferred_study_days": ["mon", "wed", "fri"],
            "preferred_study_window_start": "08:00",
            "preferred_study_window_end": "09:00",
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "07:00",
        },
    )
    assert update_response.status_code == 200
    profile = update_response.json()
    assert profile["display_name"] == "Brian"
    assert profile["preferences"]["preferred_session_minutes"] == 15
    assert profile["preferences"]["preferred_guide_mode"] == "coach"
    assert profile["preferences"]["nudge_intensity"] == "direct"
    assert profile["preferences"]["preferred_study_days"] == ["mon", "wed", "fri"]

    profile_response = client.get("/v1/users/demo-user/profile")
    assert profile_response.status_code == 200
    fetched = profile_response.json()
    assert fetched["user_id"] == "demo-user"
    assert fetched["preferences"]["preferred_translation_source_id"] == "sample_local"
    assert fetched["preferences"]["preferred_study_window_start"] == "08:00"



def test_passage_aware_questions_echo_passage_text(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    payload = start.json()
    questions = [question["question"].lower() for question in payload["session"]["questions"]]
    assert any(keyword in " ".join(questions) for keyword in ["love", "saved", "condemn", "world"])
    assert "what repeated words or themes stand out in this passage?" not in questions



def test_active_session_can_be_resumed(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    session_id = start.json()["session"]["session_id"]

    turn = client.post(
        "/v1/agent/session/respond",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "response_text": "I notice Jesus moving toward people with grace.",
            "engagement_score": 4,
        },
    )
    assert turn.status_code == 200
    assert "evaluation" in turn.json()

    resume = client.get("/v1/agent/session/active/demo-user")
    assert resume.status_code == 200
    payload = resume.json()
    assert payload["session"]["session_id"] == session_id
    assert payload["session"]["current_question_index"] == 1
    assert payload["current_question"]["type"] in {"interpretation", "application", "reflection"}
    assert payload["passage"]["source_id"] == "sample_local"



def test_action_item_is_passage_aware(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice God's love reaching toward the world.",
        "This passage shows mercy instead of condemnation.",
        "I will encourage one discouraged friend today because God moved toward me first.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
        },
    )
    assert complete.status_code == 200
    action_item = complete.json()["action_item"]
    combined = f"{action_item['title']} {action_item['detail']}".lower()
    assert any(keyword in combined for keyword in ["love", "mercy", "encourage", "john 3"])
    assert "next 24 hours" in combined or "today" in combined



def test_action_item_follow_up_is_saved(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "God is reaching toward people.",
        "The passage shows mercy is central.",
        "I should encourage a friend by tonight.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
        },
    )
    action_item_id = complete.json()["action_item"]["action_item_id"]

    follow_up = client.post(
        f"/v1/study/action-items/{action_item_id}/complete",
        json={
            "user_id": "demo-user",
            "follow_up_note": "I sent the encouragement text during lunch and prayed first.",
            "follow_up_outcome": "completed",
        },
    )
    assert follow_up.status_code == 200
    payload = follow_up.json()
    assert payload["status"] == "completed"
    assert payload["follow_up_note"].startswith("I sent the encouragement text")
    assert payload["follow_up_outcome"] == "completed"



def test_action_item_follow_up_refreshes_spiritual_memory(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "God is reaching toward people with mercy.",
        "This passage shows Christ moves first instead of condemning people.",
        "I should encourage one discouraged friend tonight.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
        },
    )
    action_item_id = complete.json()["action_item"]["action_item_id"]

    before_memory = client.get("/v1/users/demo-user/memory")
    before_payload = before_memory.json()

    follow_up = client.post(
        f"/v1/study/action-items/{action_item_id}/complete",
        json={
            "user_id": "demo-user",
            "follow_up_note": "I sent the text and then prayed for him by name.",
            "follow_up_outcome": "completed",
        },
    )
    assert follow_up.status_code == 200

    after_memory = client.get("/v1/users/demo-user/memory")
    after_payload = after_memory.json()
    assert after_payload["latest_summary"] != before_payload["latest_summary"]
    assert "completed" in after_payload["latest_summary"].lower() or "prayer" in after_payload["latest_summary"].lower()
    assert after_payload["carry_forward_prompt"] != before_payload["carry_forward_prompt"]
    assert any("completed" in theme.lower() or "follow-through" in theme.lower() for theme in after_payload["recurring_themes"])



def test_style_preferences_shape_profile_and_session_language(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    updated = client.patch(
        "/v1/users/demo-user/preferences",
        json={
            "display_name": "Brian",
            "preferred_guide_mode": "coach",
            "preferred_question_style": "practical",
            "preferred_guidance_tone": "direct",
            "preferred_translation_source_id": "sample_local",
        },
    )
    assert updated.status_code == 200
    updated_profile = updated.json()
    assert updated_profile["preferences"]["preferred_question_style"] == "practical"
    assert updated_profile["preferences"]["preferred_guidance_tone"] == "direct"

    started = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    assert started.status_code == 200
    payload = started.json()
    assert "We'll get quickly to the heart of the passage" in payload["session"]["latest_message"]
    assert any(
        question["question"].startswith("Answer plainly:") or question["question"].startswith("Make this concrete:")
        for question in payload["session"]["questions"]
    )


def test_prayer_items_can_be_created_prayed_and_answered(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    create = client.post(
        "/v1/study/prayer-items",
        json={
            "user_id": "demo-user",
            "title": "Pray for Madison",
            "detail": "Ask Christ to give Madison peace and clear wisdom this week.",
        },
    )
    assert create.status_code == 201
    prayer_item = create.json()
    prayer_item_id = prayer_item["prayer_item_id"]
    assert prayer_item["status"] == "active"

    listed = client.get("/v1/study/prayer-items/demo-user")
    assert listed.status_code == 200
    listed_items = listed.json()["items"]
    assert len(listed_items) == 1
    assert listed_items[0]["title"] == "Pray for Madison"

    prayed = client.post(
        f"/v1/study/prayer-items/{prayer_item_id}/pray",
        json={"user_id": "demo-user"},
    )
    assert prayed.status_code == 200
    assert prayed.json()["last_prayed_at"] is not None
    assert prayed.json()["status"] == "active"

    answered = client.post(
        f"/v1/study/prayer-items/{prayer_item_id}/answer",
        json={"user_id": "demo-user"},
    )
    assert answered.status_code == 200
    answered_payload = answered.json()
    assert answered_payload["status"] == "answered"
    assert answered_payload["answered_at"] is not None

    active_items = client.get("/v1/study/prayer-items/demo-user", params={"status": "active"})
    assert active_items.status_code == 200
    assert active_items.json()["items"] == []


def test_active_session_minutes_can_be_updated(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 30,
        },
    )
    assert start.status_code == 200
    session_id = start.json()["session"]["session_id"]

    first_turn = client.post(
        "/v1/agent/session/respond",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "response_text": "I notice God's love moves toward people before they can fix themselves.",
            "engagement_score": 4,
        },
    )
    assert first_turn.status_code == 200

    updated = client.post(
        "/v1/agent/session/update",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "requested_minutes": 10,
        },
    )
    assert updated.status_code == 200
    payload = updated.json()
    assert payload["session"]["requested_minutes"] == 10
    assert payload["session"]["current_question_index"] == 1
    assert len(payload["session"]["questions"]) == 2
    assert payload["current_question"] is not None
    assert [step["title"] for step in payload["session"]["plan"]] == [
        "Read Slowly",
        "Notice One Thing",
        "Answer Two Focused Questions",
        "Take One Next Step",
    ]

def test_phase_one_guided_session_flow(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "display_name": "Brian",
            "requested_minutes": 15,
            "entry_point": "I have 10 minutes",
            "text_source_id": "sample_local",
        },
    )
    assert start.status_code == 200
    started = start.json()
    session_id = started["session"]["session_id"]
    assert started["current_question"]["type"] == "observation"
    assert started["passage"]["source_id"] == "sample_local"
    assert started["recommendation"]["recommended_minutes"] >= 10

    for answer in [
        "I notice the passage centers on God's love and initiative.",
        "It shows that God moves toward people in mercy rather than condemnation.",
        "I need to encourage someone today instead of staying self-focused.",
    ]:
        turn = client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )
        assert turn.status_code == 200
        turn_payload = turn.json()
        assert "evaluation" in turn_payload
        assert turn_payload["evaluation"]["encouragement"]

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "This session reminded me to live outwardly today.",
        },
    )
    assert complete.status_code == 200
    completed = complete.json()
    assert completed["session"]["status"] == "completed"
    assert completed["action_item"]["status"] == "open"
    assert completed["engagement"]["completed_sessions"] == 1
    assert completed["engagement"]["current_streak"] == 1

    no_active = client.get("/v1/agent/session/active/demo-user")
    assert no_active.status_code == 404



def test_llm_evaluation_drives_recommendation_focus(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(WeakComprehensionProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    weak_turn = client.post(
        "/v1/agent/session/respond",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "response_text": "It is about Jesus helping people.",
            "engagement_score": 3,
        },
    )
    assert weak_turn.status_code == 200
    assert weak_turn.json()["evaluation"]["recommended_focus"] == "comprehension"

    for answer in [
        "It means Jesus walks with people and helps them see more clearly.",
        "I will encourage someone who feels discouraged today.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 3,
            },
        )

    client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
        },
    )

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    payload = recommendation.json()
    assert payload["focus_area"] == "comprehension"
    assert payload["gap_report"]["comprehension_gap"] >= payload["gap_report"]["application_gap"]
    assert "understand" in payload["reason"].lower() or "understanding" in payload["reason"].lower()



def test_strong_llm_evaluation_allows_growth_recommendation(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(StrongResponseProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 20,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice Jesus draws near to discouraged disciples and begins with their confusion.",
        "This shows Christ patiently interprets Scripture and redirects their hope toward himself.",
        "I will look for one discouraged person to encourage today because Christ moved toward his followers first.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 5,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "I want to keep tracing how Christ meets confused people in Scripture.",
            "engagement_score": 5,
        },
    )
    action_item_id = complete.json()["action_item"]["action_item_id"]
    client.post(
        f"/v1/study/action-items/{action_item_id}/complete",
        json={
            "user_id": "demo-user",
            "follow_up_note": "I encouraged a discouraged friend after this session.",
            "follow_up_outcome": "completed",
        },
    )

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    payload = recommendation.json()
    assert payload["focus_area"] == "growth"
    assert payload["recommended_guide_mode"] == "challenger"



def test_completed_session_creates_spiritual_memory(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(StrongResponseProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice Christ draws near to discouraged people and reorients them through Scripture.",
        "This passage shows Jesus patiently explaining what was already there and inviting deeper trust.",
        "I need to follow through by encouraging someone who feels confused or discouraged this week.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "Christ meets confused people patiently and I want to keep responding that way.",
        },
    )
    assert complete.status_code == 200

    memory = client.get("/v1/users/demo-user/memory")
    assert memory.status_code == 200
    memory_payload = memory.json()
    assert memory_payload["memory_count"] >= 1
    assert memory_payload["latest_summary"]
    assert memory_payload["carry_forward_prompt"]
    assert memory_payload["recurring_themes"]
    assert memory_payload["growth_areas"]
    assert memory_payload["recent_references"]

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    recommendation_payload = recommendation.json()
    assert "recent thread" in recommendation_payload["reason"].lower()
    assert recommendation_payload["recommended_entry_point"]



def test_nudge_delivery_plan_is_notification_ready(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    client.patch(
        "/v1/users/demo-user/preferences",
        json={
            "timezone": "America/New_York",
            "preferred_study_days": ["monday"],
            "preferred_study_window_start": "08:00",
            "preferred_study_window_end": "09:00",
            "quiet_hours_start": "21:00",
            "quiet_hours_end": "07:00",
        },
    )

    scheduled = client.post(
        "/v1/agent/nudges/plan",
        json={
            "user_id": "demo-user",
            "preview_at": "2026-04-06T10:00:00+00:00",
        },
    )
    assert scheduled.status_code == 200
    scheduled_payload = scheduled.json()
    assert scheduled_payload["delivery_status"] == "scheduled"
    assert scheduled_payload["delivery_channel"] == "push"
    assert scheduled_payload["deliver_at"].startswith("2026-04-06T08:00:00")

    suppressed = client.post(
        "/v1/agent/nudges/plan",
        json={
            "user_id": "demo-user",
            "preview_at": "2026-04-07T12:30:00+00:00",
        },
    )
    assert suppressed.status_code == 200
    suppressed_payload = suppressed.json()
    assert suppressed_payload["delivery_status"] == "suppressed"
    assert suppressed_payload["delivery_channel"] == "in_app"
    assert suppressed_payload["fallback_at"] is not None



def test_personalization_shared_cache_reuses_recent_response_evaluations(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    provider = CountingEvaluationProvider()
    client.app.state.container.llm_registry.register(provider)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice the passage calls me to receive the word honestly before I move too quickly.",
        "It means hearing alone is not enough; the word is meant to become obedience.",
        "Today I need to follow through on one clear act instead of staying vague.",
    ]:
        turn = client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )
        assert turn.status_code == 200

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "I want to respond to Scripture with clearer follow-through.",
        },
    )
    assert complete.status_code == 200

    personalization = client.app.state.container.personalization_service
    shared_cache = {}
    provider.evaluate_calls = 0

    recommendation = personalization.build_recommendation("demo-user", cache=shared_cache)
    style_profile = personalization.build_style_profile("demo-user", cache=shared_cache)
    preview = personalization.preview_nudge("demo-user", cache=shared_cache)

    assert recommendation.focus_area in {"application", "growth", "comprehension", "consistency"}
    assert style_profile.reason
    assert preview.title
    assert provider.evaluate_calls == 3


def test_recommendations_rotate_curated_passages_after_one_is_seen(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    service = client.app.state.container.personalization_service
    monkeypatch.setattr(
        service,
        "build_gap_report",
        lambda user_id, cache=None: StudyGapReport(
            user_id=user_id,
            comprehension_gap=0.2,
            application_gap=0.78,
            consistency_gap=0.18,
            focus_area="application",
            observed_patterns=["There are unfinished action items from prior sessions."],
        ),
    )

    first = client.get("/v1/agent/recommendations/demo-user")
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["focus_area"] == "application"
    assert first_payload["recommended_reference"] == {
        "book": "James",
        "chapter": 1,
        "start_verse": 22,
        "end_verse": 25,
    }

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200

    second = client.get("/v1/agent/recommendations/demo-user")
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["focus_area"] == "application"
    assert second_payload["recommended_reference"] != first_payload["recommended_reference"]
    assert second_payload["recommended_reference"]["book"] in {"Micah", "Colossians", "Luke", "Romans", "Ephesians", "Philippians", "1 John"}


def test_recommendations_avoid_recent_same_passage_across_focuses(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    personalization = client.app.state.container.personalization_service
    study = client.app.state.container.study_service
    monkeypatch.setattr(
        personalization,
        "build_gap_report",
        lambda user_id, cache=None: StudyGapReport(
            user_id=user_id,
            comprehension_gap=0.18,
            application_gap=0.81,
            consistency_gap=0.2,
            focus_area="application",
            observed_patterns=["A recent session still points toward clearer follow-through."],
        ),
    )

    study.record_passage_seen(
        "demo-user",
        "comprehension",
        {"book": "James", "chapter": 1, "start_verse": 22, "end_verse": 25},
    )

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    payload = recommendation.json()
    assert payload["recommended_reference"] != {
        "book": "James",
        "chapter": 1,
        "start_verse": 22,
        "end_verse": 25,
    }
    assert "bringing you back" not in payload["reason"].lower()


def test_recommendations_explain_intentional_revisits(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    personalization = client.app.state.container.personalization_service
    study = client.app.state.container.study_service
    monkeypatch.setattr(
        personalization,
        "build_gap_report",
        lambda user_id, cache=None: StudyGapReport(
            user_id=user_id,
            comprehension_gap=0.18,
            application_gap=0.81,
            consistency_gap=0.2,
            focus_area="application",
            observed_patterns=["A recent session still points toward clearer follow-through."],
        ),
    )

    for reference in CURATED_PASSAGE_BANK["application"]:
        study.record_passage_seen("demo-user", "application", reference.model_dump())

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    payload = recommendation.json()
    assert payload["recommended_reference"]["book"]
    assert "emmaus is revisiting" in payload["reason"].lower() or "emmaus is bringing you back" in payload["reason"].lower()


def test_mood_shapes_recommendation_and_nudge_preview(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    mood = client.post(
        "/v1/study/mood",
        json={
            "user_id": "demo-user",
            "mood": "stressed",
            "energy": "low",
            "notes": "Feeling overwhelmed today",
        },
    )
    assert mood.status_code == 201
    assert mood.json()["mood"] == "stressed"

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    recommendation_payload = recommendation.json()
    assert recommendation_payload["recommended_reference"]["book"] == "Psalm"
    assert recommendation_payload["recommended_minutes"] <= 10

    nudge = client.post("/v1/agent/nudges/preview", json={"user_id": "demo-user"})
    nudge_payload = nudge.json()
    assert nudge_payload["nudge_type"] == "encouragement"
    assert nudge_payload["recommended_minutes"] <= 10


def test_nudge_preview_builds_on_completed_follow_through(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(StrongResponseProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice Christ patiently meets discouraged disciples and reframes their understanding through Scripture.",
        "This means Jesus does not shame confusion but redirects it toward hope and trust in him.",
        "I will encourage one discouraged friend this week and pray with him if the moment opens.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "I want to keep following through when Christ surfaces someone to encourage.",
            "engagement_score": 4,
        },
    )
    action_item = complete.json()["action_item"]

    follow_up = client.post(
        f"/v1/study/action-items/{action_item['action_item_id']}/complete",
        json={
            "user_id": "demo-user",
            "follow_up_note": "I sent the text and prayed for him afterward.",
            "follow_up_outcome": "completed",
        },
    )
    assert follow_up.status_code == 200

    nudge = client.post("/v1/agent/nudges/preview", json={"user_id": "demo-user"})
    assert nudge.status_code == 200
    payload = nudge.json()
    assert payload["title"] == "Build on what already landed"
    assert payload["message"].startswith("You already followed through on")
    assert action_item["title"] in payload["message"]
    assert "Build on the completed step" in payload["message"] or "Christ is inviting next" in payload["message"]





def test_review_history_groups_recent_sessions_prayers_and_actions(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(StrongResponseProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 20,
        },
    )
    assert start.status_code == 200
    session_id = start.json()["session"]["session_id"]

    for answer in [
        "I notice James warns me not to stop at hearing the word without obeying it.",
        "This passage means Scripture is meant to reshape what I do, not just what I agree with.",
        "Today I need one concrete act of obedience that matches what God is showing me.",
    ]:
        turn = client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 4,
            },
        )
        assert turn.status_code == 200

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "Christ is pressing me toward clearer obedience today.",
        },
    )
    assert complete.status_code == 200
    action_item = complete.json()["action_item"]

    prayer = client.post(
        "/v1/study/prayer-items",
        json={
            "user_id": "demo-user",
            "title": "Pray for courage to obey",
            "detail": "Ask Christ to help this next step become real today.",
            "related_session_id": session_id,
        },
    )
    assert prayer.status_code == 201

    review = client.get("/v1/study/review/demo-user")
    assert review.status_code == 200
    payload = review.json()
    assert payload["user_id"] == "demo-user"
    assert len(payload["sessions"]) == 1
    entry = payload["sessions"][0]
    assert entry["session"]["session_id"] == session_id
    assert len(entry["responses"]) == 3
    assert entry["action_item"]["action_item_id"] == action_item["action_item_id"]
    assert entry["prayers"][0]["title"] == "Pray for courage to obey"
    assert entry["memory"] is not None
    assert payload["prayers"][0]["related_session_id"] == session_id


def test_look_back_prompt_and_response_are_saved(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    client.app.state.container.llm_registry.register(StrongResponseProvider())

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 15,
        },
    )
    assert start.status_code == 200
    session_id = start.json()["session"]["session_id"]
    session_reference = start.json()["session"]["reference"]

    current_question = start.json().get("current_question")
    answers = iter([
        "I notice this passage presses me to listen carefully before moving on.",
        "It shows God wants his word to shape real obedience instead of self-deception.",
        "My next step is to act on what I hear instead of only agreeing with it.",
    ])
    while current_question is not None:
        turn = client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": next(answers),
                "engagement_score": 4,
            },
        )
        assert turn.status_code == 200
        current_question = turn.json().get("next_question")

    complete = client.post(
        "/v1/agent/session/complete",
        json={
            "session_id": session_id,
            "user_id": "demo-user",
            "summary_notes": "Christ is calling me to hear the word and do it.",
        },
    )
    assert complete.status_code == 200

    look_back = client.get("/v1/study/look-back/demo-user")
    assert look_back.status_code == 200
    payload = look_back.json()
    assert payload["prompt"] is not None
    assert payload["prompt"]["session_id"] == session_id
    assert payload["prompt"]["reference"]["book"]
    assert payload["prompt"]["reference"]["chapter"] >= 1

    submit = client.post(
        "/v1/study/look-back/respond",
        json={
            "user_id": "demo-user",
            "session_id": session_id,
            "response_text": "I remember that this passage says hearing God's word should lead to real obedience.",
        },
    )
    assert submit.status_code == 201
    review = submit.json()
    assert review["session_id"] == session_id
    assert review["outcome"] in {"clear", "partial", "needs_reinforcement"}
    assert review["encouragement"]

    refreshed = client.get("/v1/study/look-back/demo-user")
    assert refreshed.status_code == 200
    refreshed_payload = refreshed.json()
    assert refreshed_payload["prompt"] is None
    assert refreshed_payload["latest_review"] is not None
    assert refreshed_payload["latest_review"]["session_id"] == session_id


def test_nudge_preview_and_plan_fall_back_to_builtin_utc_without_tzdata(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    from zoneinfo import ZoneInfoNotFoundError
    import emmaus.services.personalization as personalization_module

    def fake_zoneinfo(key):
        raise ZoneInfoNotFoundError(key)

    monkeypatch.setattr(personalization_module, 'ZoneInfo', fake_zoneinfo)

    preview_response = client.post('/v1/agent/nudges/preview', json={'user_id': 'demo-user'})
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload['local_timezone'] == 'UTC'

    plan_response = client.post('/v1/agent/nudges/plan', json={'user_id': 'demo-user'})
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert plan_payload['delivery_status'] in {'send_now', 'scheduled', 'suppressed'}


def test_requested_minutes_changes_question_count_and_plan(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    brief = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "brief-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 10,
        },
    )
    assert brief.status_code == 200
    brief_payload = brief.json()
    assert len(brief_payload["session"]["questions"]) == 2
    assert [step["title"] for step in brief_payload["session"]["plan"]] == [
        "Read Slowly",
        "Notice One Thing",
        "Answer Two Focused Questions",
        "Take One Next Step",
    ]
    assert all(step["title"] != "Use Passage Helps" for step in brief_payload["session"]["plan"])

    deep = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "deep-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 30,
        },
    )
    assert deep.status_code == 200
    deep_payload = deep.json()
    assert len(deep_payload["session"]["questions"]) == 4
    assert [step["title"] for step in deep_payload["session"]["plan"]] == [
        "Read and Pray",
        "Trace the Passage",
        "Work Through Four Questions",
        "Revisit with Passage Helps",
        "Respond and Pray",
    ]

    standard = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "standard-user",
            "text_source_id": "sample_local",
            "reference": {
                "book": "John",
                "chapter": 3,
                "start_verse": 16,
                "end_verse": 17,
            },
            "requested_minutes": 20,
        },
    )
    assert standard.status_code == 200
    standard_payload = standard.json()
    assert len(standard_payload["session"]["questions"]) == 3
    assert [step["title"] for step in standard_payload["session"]["plan"]] == [
        "Read Slowly",
        "Use Passage Helps",
        "Work Through Three Questions",
        "Respond and Pray",
    ]





def test_theme_weighted_reference_selection_prefers_service_passages(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    personalization = client.app.state.container.personalization_service

    reference = personalization._select_reference_for_focus(
        "demo-user",
        "application",
        cache={},
        preferred_themes=Counter({"service": 4, "love": 3}),
    )

    assert reference.book == "Philippians"
    assert reference.chapter == 2
    assert reference.start_verse == 3


def test_curated_passage_bank_is_expanded_for_each_focus():
    assert set(CURATED_PASSAGE_BANK) == {"consistency", "application", "comprehension", "growth"}
    assert all(len(bank) >= 8 for bank in CURATED_PASSAGE_BANK.values())






