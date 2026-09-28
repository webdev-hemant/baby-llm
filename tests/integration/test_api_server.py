"""Integration tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient
from baby_llm.api.server import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "awake"


def test_memory_lifecycle_api():
    # 1. Create a memory
    create_payload = {
        "subject": "user",
        "predicate": "prefers_theme",
        "object": "Obsidian Deep Dark",
        "category": "preference",
        "confidence": 0.98,
        "ymyl_protected": False,
    }
    create_res = client.post("/api/memories", json=create_payload)
    assert create_res.status_code == 200
    node_id = create_res.json()["id"]

    # 2. List memories
    list_res = client.get("/api/memories")
    assert list_res.status_code == 200
    memories = list_res.json()
    assert any(m["id"] == node_id for m in memories)

    # 3. Delete memory
    delete_res = client.delete(f"/api/memories/{node_id}")
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"


def test_success_compass_api():
    res = client.get("/api/success/compass")
    assert res.status_code == 200
    data = res.json()
    assert "morning_brief" in data
    assert "commitments" in data
