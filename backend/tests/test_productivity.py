import pytest
import datetime
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
        "name": "Productivity User",
        "email": "prod@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Tasks Tests
# ==========================================

def test_tasks_crud_and_filter(client, auth_headers):
    # 1. Create Task
    create_payload = {
        "title": "Finish recursion assignment",
        "description": "Solve tree traversal problems",
        "due_date": "2026-09-02T20:00:00",
        "completed": False
    }
    res = client.post("/api/tasks", json=create_payload, headers=auth_headers)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]
    assert task["title"] == "Finish recursion assignment"
    assert task["completed"] is False

    # 2. List Tasks
    list_res = client.get("/api/tasks", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Update Task to completed
    update_res = client.put(f"/api/tasks/{task_id}", json={"completed": True}, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["completed"] is True

    # 4. Filter by completed
    filter_res = client.get("/api/tasks?completed=true", headers=auth_headers)
    assert len(filter_res.json()) == 1

    filter_pending = client.get("/api/tasks?completed=false", headers=auth_headers)
    assert len(filter_pending.json()) == 0

    # 5. Delete Task
    del_res = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert len(client.get("/api/tasks", headers=auth_headers).json()) == 0


# ==========================================
# 2. Notes Tests
# ==========================================

def test_notes_crud_and_search(client, auth_headers):
    # 1. Create Notes
    client.post("/api/notes", json={
        "title": "Python Recursion Guide",
        "content": "A function that calls itself with a base condition."
    }, headers=auth_headers)

    client.post("/api/notes", json={
        "title": "SQL Query Optimization",
        "content": "Use indexes on frequently queried columns."
    }, headers=auth_headers)

    # 2. List Notes
    notes_res = client.get("/api/notes", headers=auth_headers)
    assert len(notes_res.json()) == 2

    # 3. Search Notes by Keyword
    search_res = client.get("/api/notes?q=Recursion", headers=auth_headers)
    assert len(search_res.json()) == 1
    assert "Recursion" in search_res.json()[0]["title"]
    note_id = search_res.json()[0]["id"]

    # 4. Update Note
    upd_res = client.put(f"/api/notes/{note_id}", json={"content": "Updated base condition rule."}, headers=auth_headers)
    assert upd_res.status_code == 200
    assert upd_res.json()["content"] == "Updated base condition rule."

    # 5. Delete Note
    del_res = client.delete(f"/api/notes/{note_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert len(client.get("/api/notes", headers=auth_headers).json()) == 1


# ==========================================
# 3. Reminders Tests
# ==========================================

def test_reminders_crud(client, auth_headers):
    # 1. Create Reminder
    rem_payload = {
        "title": "Submit assignment at 7 PM",
        "remind_at": "2026-09-02T19:00:00"
    }
    create_res = client.post("/api/reminders", json=rem_payload, headers=auth_headers)
    assert create_res.status_code == 201
    rem_id = create_res.json()["id"]

    # 2. List Reminders
    list_res = client.get("/api/reminders", headers=auth_headers)
    assert len(list_res.json()) == 1

    # 3. Delete Reminder
    del_res = client.delete(f"/api/reminders/{rem_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert len(client.get("/api/reminders", headers=auth_headers).json()) == 0


# ==========================================
# 4. Controlled Memory Tests
# ==========================================

def test_memory_crud_and_clear_all(client, auth_headers):
    # 1. Add Memory Items
    client.post("/api/memory", json={
        "key": "Python project path",
        "value": "Inside Projects/Python folder"
    }, headers=auth_headers)

    client.post("/api/memory", json={
        "key": "Favorite IDE",
        "value": "VS Code"
    }, headers=auth_headers)

    # 2. List Memories
    mem_res = client.get("/api/memory", headers=auth_headers)
    assert len(mem_res.json()) == 2
    mem_id = mem_res.json()[0]["id"]

    # 3. Delete Single Memory Item
    del_res = client.delete(f"/api/memory/{mem_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert len(client.get("/api/memory", headers=auth_headers).json()) == 1

    # 4. Clear All Memories
    clear_res = client.delete("/api/memory", headers=auth_headers)
    assert clear_res.status_code == 200
    assert len(client.get("/api/memory", headers=auth_headers).json()) == 0
