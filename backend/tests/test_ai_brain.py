import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.ai.intent import intent_classifier, IntentType
from backend.ai.brain import brain

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
        "name": "Dev Tester",
        "email": "tester@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Intent Classifier Unit Tests
# ==========================================

def test_intent_recursion_query():
    res = intent_classifier.classify_rule_based("Hey Sadie, explain Python recursion.")
    assert res.intent in [IntentType.CODING_ASSISTANT, IntentType.GENERAL_CONVERSATION]


def test_intent_open_app():
    res = intent_classifier.classify_rule_based("Open calculator.")
    assert res.intent == IntentType.OPEN_APPLICATION
    assert res.tool_required is True
    assert res.tool_name == "open_application"
    assert res.parameters["app_name"] == "calc.exe"


def test_intent_open_folder():
    res = intent_classifier.classify_rule_based("Open my Python project.")
    assert res.intent == IntentType.OPEN_FOLDER
    assert res.tool_required is True
    assert res.tool_name == "open_folder"
    assert "python project" in res.parameters["folder_name"].lower()


def test_intent_start_timer():
    res = intent_classifier.classify_rule_based("Start a 30 minute timer.")
    assert res.intent == IntentType.START_TIMER
    assert res.tool_required is True
    assert res.tool_name == "start_timer"
    assert res.parameters["duration_minutes"] == 30


def test_intent_study_mode():
    res = intent_classifier.classify_rule_based("Sadie, start study mode.")
    assert res.intent == IntentType.START_STUDY_MODE
    assert res.tool_required is True
    assert res.tool_name == "study_mode"


def test_intent_create_note():
    res = intent_classifier.classify_rule_based("Sadie, create a note: Study Python recursion tonight.")
    assert res.intent == IntentType.CREATE_NOTE
    assert res.tool_required is True
    assert res.tool_name == "create_note"
    assert "recursion" in res.parameters["content"].lower()


def test_intent_create_reminder_or_task():
    res = intent_classifier.classify_rule_based("Sadie, remind me to submit my assignment at 7 PM.")
    assert res.intent == IntentType.CREATE_TASK
    assert res.tool_required is True
    assert res.tool_name == "create_task"
    assert "assignment" in res.parameters["title"].lower()


def test_intent_remember_info():
    res = intent_classifier.classify_rule_based("Remember that my Python project is inside my Projects folder.")
    assert res.intent == IntentType.REMEMBER_INFO
    assert res.tool_required is True
    assert res.tool_name == "remember_info"
    assert "projects folder" in res.parameters["value"].lower()


def test_intent_system_info():
    res = intent_classifier.classify_rule_based("Show my system information.")
    assert res.intent == IntentType.GET_SYSTEM_INFO
    assert res.tool_required is True
    assert res.tool_name == "system_info"


# ==========================================
# 2. AI Brain Offline Response Unit Tests
# ==========================================

def test_brain_recursion_explanation():
    result = brain.process_message("Explain Python recursion.")
    assert "recursion" in result["response_text"].lower()
    assert "base case" in result["response_text"].lower()
    assert "```python" in result["response_text"]


# ==========================================
# 3. Assistant API Integration Tests
# ==========================================

def test_assistant_chat_endpoint(client, auth_headers):
    # Test conversational chat
    payload = {
        "message": "Hey Sadie, explain Python recursion.",
        "mode": "coding"
    }
    response = client.post("/api/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] > 0
    assert "recursion" in data["message"].lower()
    assert data["mode"] == "coding"

    conv_id = data["conversation_id"]

    # Test conversational tool request in the same conversation
    tool_payload = {
        "message": "Open calculator",
        "conversation_id": conv_id,
        "mode": "normal"
    }
    tool_res = client.post("/api/assistant/chat", json=tool_payload, headers=auth_headers)
    assert tool_res.status_code == 200
    tool_data = tool_res.json()
    assert tool_data["conversation_id"] == conv_id
    assert tool_data["tool_required"] is True
    assert tool_data["tool_name"] == "open_application"


def test_list_and_get_conversation_history(client, auth_headers):
    # Send a message
    client.post("/api/assistant/chat", json={"message": "What can you do?"}, headers=auth_headers)

    # List conversations
    conv_list = client.get("/api/assistant/conversations", headers=auth_headers)
    assert conv_list.status_code == 200
    conversations = conv_list.json()
    assert len(conversations) == 1
    conv_id = conversations[0]["id"]

    # Fetch conversation details
    detail = client.get(f"/api/assistant/conversations/{conv_id}", headers=auth_headers)
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert len(messages) == 2  # user message and sadie response
    assert messages[0]["sender"] == "user"
    assert messages[1]["sender"] == "sadie"
