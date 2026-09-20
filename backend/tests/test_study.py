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
        "name": "Study Tester",
        "email": "study@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_study_session_full_lifecycle(client, auth_headers):
    # 1. Start study session
    start_payload = {
        "subject": "Python",
        "task_name": "Recursion Practice",
        "duration_minutes": 45
    }
    start_res = client.post("/api/study/start", json=start_payload, headers=auth_headers)
    assert start_res.status_code == 200
    data = start_res.json()
    assert data["is_active"] is True
    assert data["subject"] == "Python"
    assert data["task_name"] == "Recursion Practice"
    assert data["duration_minutes"] == 45

    # 2. Check current status
    cur_res = client.get("/api/study/current", headers=auth_headers)
    assert cur_res.status_code == 200
    assert cur_res.json()["is_active"] is True
    assert cur_res.json()["subject"] == "Python"

    # 3. Pause session
    pause_res = client.post("/api/study/pause", headers=auth_headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["is_paused"] is True

    # 4. Resume session
    resume_res = client.post("/api/study/resume", headers=auth_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["is_paused"] is False

    # 5. Complete session
    comp_res = client.post("/api/study/complete", headers=auth_headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "success"

    # 6. Check history
    hist_res = client.get("/api/study/history", headers=auth_headers)
    assert hist_res.status_code == 200
    sessions = hist_res.json()
    assert len(sessions) == 1
    assert sessions[0]["completed"] is True
    assert sessions[0]["subject"] == "Python"

    # 7. Check analytics
    analytics_res = client.get("/api/study/analytics", headers=auth_headers)
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()
    assert analytics["total_study_minutes"] == 45
    assert analytics["sessions_completed"] == 1
    assert "Python" in analytics["subject_breakdown"]


def test_study_break_session(client, auth_headers):
    # Start a 5m short break
    break_res = client.post("/api/study/break", json={"break_type": "short", "duration_minutes": 5}, headers=auth_headers)
    assert break_res.status_code == 200
    data = break_res.json()
    assert data["is_active"] is True
    assert data["is_break"] is True
    assert data["duration_minutes"] == 5
