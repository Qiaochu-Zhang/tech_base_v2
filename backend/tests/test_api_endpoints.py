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
