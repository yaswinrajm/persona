from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_results() -> None:
    response = client.post(
        "/search",
        json={"name": "Rahul Sharma", "city": "Bengaluru", "company": "Infosys"},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "completed"
    assert payload["results"]
    assert any(item["decision"]["verdict"] == "same_person" for item in payload["results"])
