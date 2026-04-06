import importlib

from fastapi.testclient import TestClient


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
    assert "data-demo-scenario=\"scheduled_nudge\"" in response.text
    assert "follow-up-target-copy" in response.text
    assert "nudge-plan-card" in response.text

    asset = client.get("/static/app.js")
    assert asset.status_code == 200
    assert "demoScenario" in asset.text
    assert "buildDemoScenarioData" in asset.text
    assert "followUpOutcomeSelect" in asset.text
    assert "delivery_status" in asset.text


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


def test_active_session_can_be_resumed(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 10,
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

    resume = client.get("/v1/agent/session/active/demo-user")
    assert resume.status_code == 200
    payload = resume.json()
    assert payload["session"]["session_id"] == session_id
    assert payload["session"]["current_question_index"] == 1
    assert payload["current_question"]["type"] in {"interpretation", "application", "reflection"}
    assert payload["passage"]["source_id"] == "sample_local"


def test_action_item_follow_up_is_saved(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
            "requested_minutes": 10,
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


def test_phase_one_guided_session_flow(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "display_name": "Brian",
            "requested_minutes": 10,
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

