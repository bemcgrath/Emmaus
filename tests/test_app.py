from fastapi.testclient import TestClient

from emmaus.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_sample_passage():
    response = client.post(
        "/v1/texts/passage",
        json={
            "source_id": "sample_local",
            "book": "John",
            "chapter": 3,
            "start_verse": 16,
            "end_verse": 17,
        },
    )
    assert response.status_code == 200
    assert "For God so loved the world" in response.json()["text"]
