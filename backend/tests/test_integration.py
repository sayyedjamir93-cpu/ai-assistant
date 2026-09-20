import pytest
from unittest.mock import patch
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
        "name": "Integration Demo User",
        "email": "demo@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# End-to-End Demonstration Scenario Tests
# ==========================================

@patch("backend.api.voice.tts_engine.synthesize_to_bytes")
def test_full_demo_scenario(mock_tts, client, auth_headers):
    """Executes the complete 8-step College PBL Demo Scenario."""
    mock_tts.return_value = {
        "success": True,
        "spoken_text": "Sample speech",
        "audio_base64": "data:audio/mpeg;base64,SUQzBAAAAAAA...",
        "mime_type": "audio/mpeg",
        "size_bytes": 1024
    }

    # 1. User logs in & checks profile
    me_res = client.get("/api/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Integration Demo User"


    # 2. User says: "Sadie, start study mode."
    study_voice = client.post("/api/voice/chat", json={
        "text_fallback": "Sadie, start study mode.",
        "mode": "study",
        "synthesize_voice": True
    }, headers=auth_headers)
    assert study_voice.status_code == 200
    assert study_voice.json()["intent"] == "START_STUDY_MODE"
    assert study_voice.json()["audio_base64"] is not None

    # Verify study session started
    study_cur = client.get("/api/study/current", headers=auth_headers)
    assert study_cur.status_code == 200

    # 3. User says: "Explain Python recursion."
    explain_voice = client.post("/api/voice/chat", json={
        "text_fallback": "Hey Sadie, explain Python recursion.",
        "mode": "coding",
        "synthesize_voice": True
    }, headers=auth_headers)
    assert explain_voice.status_code == 200
    assert "recursion" in explain_voice.json()["response_text"].lower()
    assert explain_voice.json()["audio_base64"] is not None

    # 4. User says: "Start a 30 minute timer."
    timer_voice = client.post("/api/voice/chat", json={
        "text_fallback": "Start a 30 minute timer",
        "mode": "normal",
        "synthesize_voice": True
    }, headers=auth_headers)
    assert timer_voice.status_code == 200
    assert timer_voice.json()["intent"] == "START_TIMER"
    assert timer_voice.json()["tool_executed"] == "start_timer"

    # 5. User says: "Open my Python project."
    with patch("os.startfile"):
        folder_voice = client.post("/api/voice/chat", json={
            "text_fallback": "Open my Python project",
            "mode": "normal",
            "synthesize_voice": True
        }, headers=auth_headers)
        assert folder_voice.status_code == 200
        assert folder_voice.json()["intent"] == "OPEN_FOLDER"
        assert folder_voice.json()["tool_executed"] == "open_folder"

    # 6. User says: "Open calculator."
    with patch("subprocess.Popen"):
        calc_voice = client.post("/api/voice/chat", json={
            "text_fallback": "Open calculator",
            "mode": "normal",
            "synthesize_voice": True
        }, headers=auth_headers)
        assert calc_voice.status_code == 200
        assert calc_voice.json()["intent"] == "OPEN_APPLICATION"
        assert calc_voice.json()["tool_executed"] == "open_application"

    # 7. User creates a note using voice: "Create a note: Study Python recursion tonight"
    note_voice = client.post("/api/voice/chat", json={
        "text_fallback": "Create a note: Study Python recursion tonight",
        "mode": "normal",
        "synthesize_voice": True
    }, headers=auth_headers)
    assert note_voice.status_code == 200
    assert note_voice.json()["intent"] == "CREATE_NOTE"

    # Verify note creation directly via Notes API
    note_create = client.post("/api/notes", json={
        "title": "Python Recursion Tonight",
        "content": "Study base cases and tree traversals."
    }, headers=auth_headers)
    assert note_create.status_code == 201
    notes_list = client.get("/api/notes", headers=auth_headers)
    assert len(notes_list.json()) >= 1

    # 8. User opens productivity dashboard & completes study session
    comp_res = client.post("/api/study/complete", headers=auth_headers)
    assert comp_res.status_code == 200
    analytics_res = client.get("/api/study/analytics", headers=auth_headers)
    assert analytics_res.status_code == 200
    assert "total_study_minutes" in analytics_res.json()
