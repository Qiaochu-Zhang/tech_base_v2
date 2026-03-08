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


def test_draft_with_empty_indicator_value_can_publish():
    draft_payload = {
        "title": "空指标值草稿",
        "content": "这是带空指标值的草稿正文",
        "source_url": "https://example.com/empty-indicator",
        "published_at": "2026-03-08T00:00:00Z",
        "importance_score": 3,
        "is_new_tech": False,
        "comment": "允许指标值为空",
        "source_types": ["产业新闻"],
        "info_types": ["技术"],
        "tags": ["回归"],
        "domain_ids": ["DOM_CCUS_CAPTURE_SOLID_SORBENT"],
        "classification": "内部",
        "status": "draft",
        "draft_data": {
            "manual_alert": False,
            "duration": "month",
            "indicators": [
                {"name": "工作容量", "value": "", "unit": "mmol/g", "keep": True},
                {"name": "再生能耗", "value": "2.1", "unit": "GJ/tCO2", "keep": True},
            ],
        },
        "alert": None,
    }
    draft_resp = client.post("/api/info-items/draft", json=draft_payload)
    assert draft_resp.status_code == 201
    draft = draft_resp.json()
    assert draft["status"] == "draft"

    publish_payload = {
        "title": draft_payload["title"],
        "content": draft_payload["content"],
        "source_url": draft_payload["source_url"],
        "published_at": draft_payload["published_at"],
        "importance_score": draft_payload["importance_score"],
        "is_new_tech": draft_payload["is_new_tech"],
        "comment": draft_payload["comment"],
        "source_types": draft_payload["source_types"],
        "info_types": draft_payload["info_types"],
        "tags": draft_payload["tags"],
        "domain_ids": draft_payload["domain_ids"],
        "classification": draft_payload["classification"],
        "draft_id": draft["id"],
        "alert": None,
    }
    publish_resp = client.post("/api/info-items/publish", json=publish_payload)
    assert publish_resp.status_code == 201
    published = publish_resp.json()
    assert published["status"] == "published"
