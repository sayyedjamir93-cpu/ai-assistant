import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.voice.speech_to_text import stt_engine
from backend.voice.text_to_speech import tts_engine

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
        "name": "Voice Tester",
        "email": "voice@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Voice Engine Unit Tests
# ==========================================

def test_tts_clean_text_for_speech():
    raw_markdown = "Here is the code: ```python\ndef hello():\n    print('Hi')\n```. Check `variable_name`."
    cleaned = tts_engine.clean_text_for_speech(raw_markdown)
    assert "```" not in cleaned
    assert "Code snippet provided on screen" in cleaned
    assert "variable_name" in cleaned


def test_tts_synthesis_to_bytes():
    res = tts_engine.synthesize_to_bytes("Hello from Sadie AI!")
    assert res["success"] is True
    assert res["audio_base64"].startswith("data:audio/mpeg;base64,")
    assert res["mime_type"] == "audio/mpeg"


def test_stt_empty_payload_error():
    res = stt_engine.transcribe_audio_bytes(b"")
    assert res["success"] is False
    assert "empty" in res["error"].lower()


# ==========================================
# 2. Voice API Integration Tests
# ==========================================

def test_voice_synthesize_endpoint(client):
    res = client.post("/api/voice/synthesize", json={"text": "Calculator is open."})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "audio_base64" in data
    assert data["spoken_text"] == "Calculator is open."


def test_voice_chat_pipeline_with_tool(client, auth_headers):
    # Simulate voice request: "Open calculator"
    payload = {
        "text_fallback": "Open calculator",
        "mode": "normal",
        "synthesize_voice": True
    }
    with patch("subprocess.Popen"):
        response = client.post("/api/voice/chat", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["transcribed_text"] == "Open calculator"
        assert data["intent"] == "OPEN_APPLICATION"
        assert data["tool_executed"] == "open_application"
        assert data["conversation_id"] > 0
        assert data["audio_base64"] is not None


def test_voice_chat_pipeline_educational_query(client, auth_headers):
    # Simulate voice request: "Explain Python recursion"
    payload = {
        "text_fallback": "Explain Python recursion",
        "mode": "coding",
        "synthesize_voice": True
    }
    response = client.post("/api/voice/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "recursion" in data["response_text"].lower()
    assert data["intent"] in ["CODING_ASSISTANT", "GENERAL_CONVERSATION"]
    assert data["audio_base64"] is not None
