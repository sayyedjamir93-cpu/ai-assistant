import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.ai.intent import IntentClassifier, IntentType
from backend.tools.vscode_creator import create_and_open_in_vscode, generate_code_content, get_vscode_executable
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
        "name": "Code Developer",
        "email": "dev@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


intent_classifier = IntentClassifier()


# ==========================================
# 1. VS Code Creator Unit Tests
# ==========================================

def test_create_python_sum_program():
    with patch("subprocess.Popen") as mock_popen:
        res = create_and_open_in_vscode(
            language="python",
            task_description="sum of two numbers",
            open_editor=True
        )
        assert res["success"] is True
        assert res["language"] == "python"
        assert res["filename"].endswith(".py")
        assert "calculate_sum" in res["code"]
        assert "SADIE PYTHON SUM CALCULATOR" in res["code"]


def test_create_cpp_fibonacci_program():
    with patch("subprocess.Popen") as mock_popen:
        res = create_and_open_in_vscode(
            language="cpp",
            task_description="fibonacci",
            open_editor=True
        )
        assert res["success"] is True
        assert res["language"] == "cpp"
        assert res["filename"].endswith(".cpp")
        assert "#include <iostream>" in res["code"]


def test_create_javascript_calculator():
    with patch("subprocess.Popen") as mock_popen:
        res = create_and_open_in_vscode(
            language="javascript",
            task_description="calculator",
            open_editor=True
        )
        assert res["success"] is True
        assert res["language"] == "javascript"
        assert res["filename"].endswith(".js")
        assert "readline" in res["code"]


def test_create_html_web_app():
    with patch("subprocess.Popen") as mock_popen:
        res = create_and_open_in_vscode(
            language="html",
            task_description="weather app",
            open_editor=False
        )
        assert res["success"] is True
        assert res["language"] == "html"
        assert res["filename"].endswith(".html")
        assert "<!DOCTYPE html>" in res["code"]


# ==========================================
# 2. Intent Classifier Pattern Matching Tests
# ==========================================

def test_intent_create_sum_program_on_python_language():
    intent = intent_classifier.classify_rule_based("create sum program on python language")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.tool_name == "create_code_file"
    assert intent.parameters["language"] == "python"
    assert "sum" in intent.parameters["task_description"].lower()


def test_intent_create_sum_program_in_python():
    intent = intent_classifier.classify_rule_based("create sum program in python")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.parameters["language"] == "python"


def test_intent_open_vscode_and_create_sum_program():
    intent = intent_classifier.classify_rule_based("open vs code and create sum program on python")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.parameters["language"] == "python"


def test_intent_create_python_program_to_calculate_sum():
    intent = intent_classifier.classify_rule_based("create python program to calculate sum of two numbers")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.parameters["language"] == "python"
    assert "sum" in intent.parameters["task_description"].lower()


def test_intent_write_fibonacci_in_cpp():
    intent = intent_classifier.classify_rule_based("write a fibonacci program in c++")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.parameters["language"] == "cpp"


def test_intent_create_calculator_in_javascript():
    intent = intent_classifier.classify_rule_based("create a calculator in javascript")
    assert intent.intent == IntentType.CREATE_PROGRAM
    assert intent.tool_required is True
    assert intent.parameters["language"] == "javascript"


# ==========================================
# 3. API & Tool Router Integration Tests
# ==========================================

def test_tool_execute_create_code_file_endpoint(client, auth_headers):
    with patch("subprocess.Popen"):
        payload = {
            "tool_name": "create_code_file",
            "parameters": {
                "language": "python",
                "task_description": "sum of two numbers",
                "open_editor": False
            }
        }
        res = client.post("/api/tools/execute", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["tool_name"] == "create_code_file"
        assert "sum" in data["result"]["filename"]
        assert "calculate_sum" in data["result"]["code"]


def test_assistant_chat_create_program_flow(client, auth_headers):
    with patch("subprocess.Popen"):
        res = client.post(
            "/api/assistant/chat",
            json={"message": "create sum program on python language"},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "CREATE_PROGRAM"
        assert data["tool_required"] is True
        assert data["tool_name"] == "create_code_file"
        assert "PYTHON" in data["message"] or "VS Code" in data["message"]


def test_voice_chat_create_program_flow(client, auth_headers):
    with patch("subprocess.Popen"):
        res = client.post(
            "/api/voice/chat",
            json={"text_fallback": "create sum program in python", "synthesize_voice": False},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "CREATE_PROGRAM"
        assert data["tool_executed"] == "create_code_file"
        assert "VS Code" in data["response_text"]
