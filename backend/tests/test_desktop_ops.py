import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.tools.app_launcher import launch_application
from backend.ai.intent import IntentClassifier, IntentType
from backend.ai.tool_router import tool_router


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
        "name": "Laptop User",
        "email": "laptop@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


intent_classifier = IntentClassifier()


# ==========================================
# 1. Desktop & Web Tool Tests
# ==========================================

def test_launch_chatgpt_with_query():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = launch_application(app_name="chatgpt", query="how to code python")
        assert res["success"] is True
        assert res["app_name"] == "ChatGPT"
        assert "chatgpt.com" in res["executable"]
        assert mock_start.called or mock_popen.called or mock_open.called


def test_launch_google_with_query():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = launch_application(app_name="google", query="today weather")
        assert res["success"] is True
        assert res["app_name"] == "Google"
        assert "google.com/search" in res["executable"]
        assert mock_start.called or mock_popen.called or mock_open.called


def test_launch_gmail():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = launch_application(app_name="gmail")
        assert res["success"] is True
        assert res["app_name"] == "Gmail"
        assert "mail.google.com" in res["executable"]


def test_launch_lock_screen():
    with patch("subprocess.Popen") as mock_popen:
        res = launch_application(app_name="lock")
        assert res["success"] is True
        assert "Lock" in res["app_name"]


def test_launch_word_excel_powerpoint():
    with patch("subprocess.Popen"):
        res_word = launch_application(app_name="word")
        assert res_word["success"] is True
        assert res_word["executable"] == "winword.exe"

        res_excel = launch_application(app_name="excel")
        assert res_excel["success"] is True
        assert res_excel["executable"] == "excel.exe"

        res_ppt = launch_application(app_name="powerpoint")
        assert res_ppt["success"] is True
        assert res_ppt["executable"] == "powerpnt.exe"


# ==========================================
# 2. Intent Classification Tests
# ==========================================

def test_intent_ask_chatgpt():
    intent = intent_classifier.classify_rule_based("ask chatgpt how to create a react app")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "chatgpt"
    assert "react" in intent.parameters.get("query", "").lower()


def test_intent_search_google():
    intent = intent_classifier.classify_rule_based("search google for python tutorial")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "google"
    assert "python" in intent.parameters.get("query", "").lower()


def test_intent_open_mail():
    intent = intent_classifier.classify_rule_based("open mail")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "mail"


def test_intent_check_my_mails():
    intent = intent_classifier.classify_rule_based("check my mails")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "mail"

    intent2 = intent_classifier.classify_rule_based("check emails")
    assert intent2.intent == IntentType.OPEN_APPLICATION
    assert intent2.tool_name == "open_app"


def test_intent_open_chrome():
    intent = intent_classifier.classify_rule_based("open chrome")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "chrome"

    intent2 = intent_classifier.classify_rule_based("sadie open chrome")
    assert intent2.intent == IntentType.OPEN_APPLICATION
    assert intent2.parameters["app_name"] == "chrome"


def test_intent_open_gmail():
    intent = intent_classifier.classify_rule_based("open gmail")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "gmail"


def test_intent_open_files():
    intent = intent_classifier.classify_rule_based("open files")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert "explorer" in intent.parameters["app_name"]


def test_intent_lock_laptop():
    intent = intent_classifier.classify_rule_based("lock my laptop")
    assert intent.intent == IntentType.OPEN_APPLICATION
    assert intent.tool_name == "open_app"
    assert intent.parameters["app_name"] == "lock"


# ==========================================
# 3. Chat & Voice Pipeline Tests
# ==========================================

def test_assistant_chat_google_command(client, auth_headers):
    with patch("webbrowser.open"):
        res = client.post(
            "/api/assistant/chat",
            json={"message": "search google for latest ai news"},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "OPEN_APPLICATION"
        assert data["tool_name"] == "open_app"
