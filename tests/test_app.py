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
    assert "Emmaus" in response.text

    asset = client.get("/static/app.js")
    assert asset.status_code == 200
    assert "loadDashboard" in asset.text


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
            "timezone": "America/New_York",
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
    assert profile["preferences"]["timezone"] == "America/New_York"

    profile_response = client.get("/v1/users/demo-user/profile")
    assert profile_response.status_code == 200
    fetched = profile_response.json()
    assert fetched["user_id"] == "demo-user"
    assert fetched["preferences"]["preferred_translation_source_id"] == "sample_local"
    assert fetched["preferences"]["preferred_study_window_start"] == "08:00"


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

    action_items = client.get("/v1/study/action-items/demo-user")
    assert action_items.status_code == 200
    assert len(action_items.json()["items"]) == 1

    streaks = client.get("/v1/engagement/streaks/demo-user")
    assert streaks.status_code == 200
    assert streaks.json()["completed_sessions"] == 1
    assert streaks.json()["current_streak"] == 1


def test_recommendation_targets_application_gaps(tmp_path, monkeypatch):
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
        "Love.",
        "It means God is good.",
        "I should do better.",
    ]:
        client.post(
            "/v1/agent/session/respond",
            json={
                "session_id": session_id,
                "user_id": "demo-user",
                "response_text": answer,
                "engagement_score": 2,
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
    assert payload["focus_area"] == "application"
    assert payload["recommended_guide_mode"] in {"coach", "peer"}
    assert payload["gap_report"]["application_gap"] >= payload["gap_report"]["comprehension_gap"]

    next_start = client.post(
        "/v1/agent/session/start",
        json={
            "user_id": "demo-user",
            "text_source_id": "sample_local",
        },
    )
    assert next_start.status_code == 200
    next_payload = next_start.json()
    assert next_payload["recommendation"]["focus_area"] == "application"
    assert next_payload["session"]["guide_mode"] in {"coach", "peer"}


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

    latest_mood = client.get("/v1/study/mood/demo-user")
    assert latest_mood.status_code == 200
    assert latest_mood.json()["energy"] == "low"

    recommendation = client.get("/v1/agent/recommendations/demo-user")
    assert recommendation.status_code == 200
    recommendation_payload = recommendation.json()
    assert recommendation_payload["recommended_reference"]["book"] == "Psalm"
    assert recommendation_payload["recommended_minutes"] <= 10
    assert recommendation_payload["recommended_entry_point"] == "I need encouragement"

    nudge = client.post("/v1/agent/nudges/preview", json={"user_id": "demo-user"})
    assert nudge.status_code == 200
    nudge_payload = nudge.json()
    assert nudge_payload["nudge_type"] == "encouragement"
    assert nudge_payload["recommended_minutes"] <= 10
    assert nudge_payload["recommendation"]["recommended_reference"]["book"] == "Psalm"


def test_nudge_timing_respects_windows_and_quiet_hours(tmp_path, monkeypatch):
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

    later_today = client.post(
        "/v1/agent/nudges/preview",
        json={
            "user_id": "demo-user",
            "preview_at": "2026-04-06T10:00:00+00:00",
        },
    )
    assert later_today.status_code == 200
    later_payload = later_today.json()
    assert later_payload["timing_decision"] == "later_today"
    assert later_payload["local_timezone"] == "America/New_York"
    assert later_payload["scheduled_for"].startswith("2026-04-06T08:00:00")

    now_response = client.post(
        "/v1/agent/nudges/preview",
        json={
            "user_id": "demo-user",
            "preview_at": "2026-04-06T12:30:00+00:00",
        },
    )
    assert now_response.status_code == 200
    now_payload = now_response.json()
    assert now_payload["timing_decision"] == "now"

    not_today = client.post(
        "/v1/agent/nudges/preview",
        json={
            "user_id": "demo-user",
            "preview_at": "2026-04-07T12:30:00+00:00",
        },
    )
    assert not_today.status_code == 200
    not_today_payload = not_today.json()
    assert not_today_payload["timing_decision"] == "not_today"
