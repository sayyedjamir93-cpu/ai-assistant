import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "SADIE"
    assert data["status"] == "online"
    assert "documentation" in data


def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["app_name"] == "SADIE"
    assert "database" in data
    assert data["database"]["status"] == "healthy"
    assert "system" in data
    assert "cpu_usage_percent" in data["system"]
