import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.tools.app_launcher import launch_application
from backend.tools.folder_launcher import launch_folder
from backend.tools.web_search import search_web
from backend.tools.timer import start_countdown_timer
from backend.tools.system_info import get_safe_system_info
from backend.ai.tool_router import tool_router

# In-memory SQLite with StaticPool
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
        "name": "Tool Tester",
        "email": "tools@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Tool Functions Unit Tests
# ==========================================

def test_app_launcher_security_rejection():
    # Attempting to launch non-allowlisted program
    res = launch_application("format_hard_drive.exe")
    assert res["success"] is False
    assert "Security restriction" in res["error"]


def test_app_launcher_allowed_mock():
    with patch("subprocess.Popen") as mock_popen, patch("shutil.which", return_value="calc.exe"):
        res = launch_application("calculator")
        assert res["success"] is True
        assert res["executable"] == "calc.exe"
        assert mock_popen.called


def test_folder_launcher_security_rejection():
    # Attempting to open unauthorized path
    res = launch_folder("C:/Windows/System32/drivers/etc")
    assert res["success"] is False
    assert "Security restriction" in res["error"]


def test_folder_launcher_allowed_mock():
    with patch("os.startfile") as mock_startfile:
        res = launch_folder("Projects")
        assert res["success"] is True
        assert "Projects" in res["path"]


def test_web_search():
    res = search_web("Python recursion tutorial")
    assert res["success"] is True
    assert len(res["results"]) > 0
    assert "title" in res["results"][0]
    assert "summary" in res["results"][0]
    assert "url" in res["results"][0]


def test_start_countdown_timer():
    res = start_countdown_timer(duration_minutes=15, label="Focus Sprint")
    assert res["success"] is True
    assert res["timer"]["duration_minutes"] == 15
    assert res["timer"]["label"] == "Focus Sprint"
    assert "ends_at" in res["timer"]


def test_system_info():
    info = get_safe_system_info()
    assert info["success"] is True
    assert "application" in info
    assert info["application"]["name"] == "SADIE"
    assert "cpu" in info
    assert "memory" in info
    assert "storage" in info
    assert "total_gb" in info["memory"]


# ==========================================
# 2. Tools API Integration Tests
# ==========================================

def test_list_tools_endpoint(client):
    res = client.get("/api/tools")
    assert res.status_code == 200
    tools = res.json()
    tool_names = [t["name"] for t in tools]
    assert "open_application" in tool_names
    assert "open_folder" in tool_names
    assert "web_search" in tool_names
    assert "start_timer" in tool_names
    assert "system_info" in tool_names


def test_system_info_endpoint(client):
    res = client.get("/api/system/info")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["application"]["name"] == "SADIE"


def test_execute_tool_timer(client, auth_headers):
    payload = {
        "tool_name": "start_timer",
        "parameters": {"duration_minutes": 25, "label": "Pomodoro Session"}
    }
    res = client.post("/api/tools/execute", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["tool_name"] == "start_timer"


def test_tool_permissions_toggle(client, auth_headers):
    # Check default permissions
    perm_res = client.get("/api/tools/permissions", headers=auth_headers)
    assert perm_res.status_code == 200
    perms = perm_res.json()
    app_perm = next(p for p in perms if p["tool_name"] == "open_application")
    assert app_perm["is_allowed"] is True

    # Disable permission for open_application
    update_res = client.put(
        "/api/tools/permissions/open_application",
        json={"is_allowed": False},
        headers=auth_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["is_allowed"] is False

    # Attempt to execute tool now -> Expect 400 Permission Denied
    exec_res = client.post(
        "/api/tools/execute",
        json={"tool_name": "open_application", "parameters": {"app_name": "calc.exe"}},
        headers=auth_headers
    )
    assert exec_res.status_code == 400
    assert "Permission Denied" in exec_res.json()["detail"]

    # Re-enable permission
    client.put(
        "/api/tools/permissions/open_application",
        json={"is_allowed": True},
        headers=auth_headers
    )
