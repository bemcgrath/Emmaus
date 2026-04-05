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
        },
    )
    assert update_response.status_code == 200
    profile = update_response.json()
    assert profile["display_name"] == "Brian"
    assert profile["preferences"]["preferred_session_minutes"] == 15
    assert profile["preferences"]["preferred_guide_mode"] == "coach"

    profile_response = client.get("/v1/users/demo-user/profile")
    assert profile_response.status_code == 200
    fetched = profile_response.json()
    assert fetched["user_id"] == "demo-user"
    assert fetched["preferences"]["preferred_translation_source_id"] == "sample_local"


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
