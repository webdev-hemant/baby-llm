"""Integration tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient
from baby_llm.api.server import app

client = TestClient(app)


def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text or "Baby LLM" in response.text


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


def test_manifest_endpoint():
    res = client.get("/manifest.json")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Baby LLM"
    assert data["display"] == "standalone"


def test_memory_update_api():
    # 1. Create initial memory
    create_payload = {
        "subject": "user",
        "predicate": "lives_in",
        "object": "Seattle",
        "category": "lifestyle",
    }
    create_res = client.post("/api/memories", json=create_payload)
    assert create_res.status_code == 200
    node_id = create_res.json()["id"]

    # 2. Update memory in-place via PUT
    update_payload = {
        "object": "Austin",
        "category": "lifestyle",
    }
    update_res = client.put(f"/api/memories/{node_id}", json=update_payload)
    assert update_res.status_code == 200
    update_data = update_res.json()
    assert update_data["status"] == "updated"
    assert "Austin" in update_data["fact"]


def test_chat_incognito_bypasses_wal():
    from baby_llm.storage.wal import wal_logger

    initial_count = len(wal_logger.get_unprocessed_turns())
    res = client.post(
        "/api/chat",
        json={
            "message": "Temporary secret question that should not be persisted",
            "incognito": True,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["incognito"] is True
    assert data["turn_id"] is None
    # Verify WAL turn count did not increase
    assert len(wal_logger.get_unprocessed_turns()) == initial_count
