from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_domains_tree_ok():
    response = client.get("/api/domains/tree")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        first = payload[0]
        assert "id" in first
        assert "name" in first
        assert "children" in first


def test_info_items_ok():
    response = client.get("/api/info-items")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        first = payload[0]
        assert "id" in first
        assert "title" in first


def test_draft_create_and_get_ok():
    payload = {
        "title": "测试草稿",
        "content": "测试正文",
        "source_url": "https://example.com",
        "published_at": "2026-03-07T00:00:00Z",
        "importance_score": 4,
        "is_new_tech": True,
        "comment": "测试备注",
        "source_types": ["产业新闻"],
        "info_types": ["技术"],
        "tags": ["测试"],
        "domain_ids": ["DOM_CCUS_CAPTURE_SOLID_SORBENT"],
        "classification": "内部",
        "status": "draft",
        "draft_data": {"manual_alert": False, "duration": "month", "indicators": []},
        "alert": None,
    }
    create_resp = client.post("/api/info-items/draft", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["status"] == "draft"
    assert created["domain_ids"] == ["DOM_CCUS_CAPTURE_SOLID_SORBENT"]

    draft_id = created["id"]
    get_resp = client.get(f"/api/info-items/{draft_id}/draft")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == draft_id
    assert "draft_data" in fetched
