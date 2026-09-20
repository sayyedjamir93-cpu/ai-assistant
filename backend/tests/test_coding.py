import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db

# In-memory SQLite
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    reg = client.post("/api/auth/register", json={
        "name": "Coder User",
        "email": "coder@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_explain_concept_endpoint(client, auth_headers):
    payload = {
        "concept": "Recursion",
        "language": "python"
    }
    res = client.post("/api/coding/explain-concept", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["concept"] == "Recursion"
    assert data["language"] == "python"
    assert "recursion" in data["explanation"].lower()
    assert len(data["best_practices"]) > 0


def test_diagnose_index_error(client, auth_headers):
    payload = {
        "error_message": "IndexError: list index out of range",
        "language": "python",
        "code_snippet": "arr = [1, 2]\nprint(arr[5])"
    }
    res = client.post("/api/coding/diagnose-error", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["error_name"] == "IndexError"
    assert len(data["possible_causes"]) > 0
    assert len(data["how_to_fix"]) > 0
    assert "len(" in data["code_example"]


def test_diagnose_type_error(client, auth_headers):
    payload = {
        "error_message": "TypeError: can only concatenate str (not 'int') to str",
        "language": "python"
    }
    res = client.post("/api/coding/diagnose-error", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["error_name"] == "TypeError"
    assert "incompatible" in data["meaning"].lower() or "type" in data["meaning"].lower()


def test_review_code_endpoint(client, auth_headers):
    payload = {
        "code": "def calculate_total(prices):\n    total = 0\n    for p in prices:\n        total += p\n    return total",
        "language": "python"
    }
    res = client.post("/api/coding/review-code", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["lines_analyzed"] == 5
    assert len(data["recommendations"]) > 0


def test_supported_languages(client):
    res = client.get("/api/coding/languages")
    assert res.status_code == 200
    data = res.json()
    lang_ids = [l["id"] for l in data["supported_languages"]]
    assert "python" in lang_ids
    assert "javascript" in lang_ids
    assert "c" in lang_ids
    assert "cpp" in lang_ids
