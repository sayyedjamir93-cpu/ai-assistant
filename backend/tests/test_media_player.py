import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.tools.media_player import play_media
from backend.ai.intent import intent_classifier, IntentType
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
        "name": "Media Tester",
        "email": "media@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Media Player Unit Tests
# ==========================================

def test_play_youtube_with_song():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = play_media(platform="youtube", query="Bohemian Rhapsody")
        assert res["success"] is True
        assert res["platform"] == "youtube"
        assert res["query"] == "Bohemian Rhapsody"
        assert "youtube.com" in res["url"]
        assert "Playing 'Bohemian Rhapsody' on YouTube" in res["message"]
        assert mock_start.called or mock_popen.called or mock_open.called


def test_open_youtube_homepage():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = play_media(platform="youtube", query="")
        assert res["success"] is True
        assert res["platform"] == "youtube"
        assert res["url"] == "https://www.youtube.com"
        assert "Opened YouTube" in res["message"]
        assert mock_start.called or mock_popen.called or mock_open.called


def test_play_spotify_with_song():
    with patch("webbrowser.open") as mock_browser, patch("os.startfile") as mock_startfile:
        res = play_media(platform="spotify", query="Starboy")
        assert res["success"] is True
        assert res["platform"] == "spotify"
        assert res["query"] == "Starboy"
        assert "spotify:search:Starboy" in res["uri"]
        assert "Playing 'Starboy'" in res["message"]


def test_open_spotify_home():
    with patch("webbrowser.open") as mock_browser, patch("os.startfile") as mock_startfile:
        res = play_media(platform="spotify", query="")
        assert res["success"] is True
        assert res["platform"] == "spotify"
        assert res["uri"] == "spotify:"
        assert res["url"] == "https://open.spotify.com"
        assert "Opened Spotify" in res["message"]


# ==========================================
# 2. Intent Classifier Pattern Matching Tests
# ==========================================

def test_intent_open_youtube_and_play():
    intent = intent_classifier.classify_rule_based("open youtube and play bohemian rhapsody")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.tool_name == "play_media"
    assert intent.parameters["platform"] == "youtube"
    assert "bohemian rhapsody" in intent.parameters["query"].lower()


def test_intent_play_on_spotify():
    intent = intent_classifier.classify_rule_based("play starboy on spotify")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.tool_name == "play_media"
    assert intent.parameters["platform"] == "spotify"
    assert "starboy" in intent.parameters["query"].lower()


def test_intent_play_video_on_youtube():
    intent = intent_classifier.classify_rule_based("play python tutorial video on youtube")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["platform"] == "youtube"
    assert "python tutorial" in intent.parameters["query"].lower()


def test_intent_open_spotify():
    intent = intent_classifier.classify_rule_based("open spotify")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["platform"] == "spotify"
    assert intent.parameters["query"] == ""


def test_intent_open_youtube():
    intent = intent_classifier.classify_rule_based("open youtube")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["platform"] == "youtube"
    assert intent.parameters["query"] == ""


def test_intent_search_youtube_for():
    intent = intent_classifier.classify_rule_based("search youtube for machine learning")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["platform"] == "youtube"
    assert "machine learning" in intent.parameters["query"].lower()


def test_intent_search_spotify_for():
    intent = intent_classifier.classify_rule_based("search spotify for lofi beats")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["platform"] == "spotify"
    assert "lofi beats" in intent.parameters["query"].lower()


def test_intent_generic_play_song():
    intent = intent_classifier.classify_rule_based("play despacito")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert "despacito" in intent.parameters["query"].lower()


def test_intent_suggest_song():
    intent = intent_classifier.classify_rule_based("suggest me a song")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.tool_name == "play_media"
    assert len(intent.parameters["query"]) > 0
    assert "recommend" in intent.suggested_response.lower() or "playing" in intent.suggested_response.lower()


def test_intent_play_a_song_for_me():
    intent = intent_classifier.classify_rule_based("play a song for me")
    assert intent.intent == IntentType.PLAY_MEDIA
    assert intent.tool_required is True
    assert intent.tool_name == "play_media"
    assert len(intent.parameters["query"]) > 0


# ==========================================
# 3. API Endpoints Integration Tests
# ==========================================

def test_tool_execute_play_media_endpoint(client, auth_headers):
    with patch("webbrowser.open"):
        payload = {
            "tool_name": "play_media",
            "parameters": {"platform": "youtube", "query": "Inception Soundtrack"}
        }
        res = client.post("/api/tools/execute", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["tool_name"] == "play_media"
        assert data["result"]["platform"] == "youtube"


def test_assistant_chat_media_command(client, auth_headers):
    with patch("webbrowser.open"):
        res = client.post(
            "/api/assistant/chat",
            json={"message": "play Bohemian Rhapsody on Spotify"},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "PLAY_MEDIA"
        assert data["tool_required"] is True
        assert data["tool_name"] == "play_media"
        assert "Bohemian Rhapsody" in data["message"]


def test_voice_chat_media_command(client, auth_headers):
    with patch("webbrowser.open"):
        res = client.post(
            "/api/voice/chat",
            json={"text_fallback": "open youtube and play python tutorial", "synthesize_voice": False},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["intent"] == "PLAY_MEDIA"
        assert data["tool_executed"] == "play_media"
        assert "YouTube" in data["response_text"]


# ==========================================
# 4. Windows Native Media Control Tests
# ==========================================

def test_intent_control_media_pause():
    intent = intent_classifier.classify_rule_based("pause the music")
    assert intent.intent == IntentType.CONTROL_MEDIA
    assert intent.tool_required is True
    assert intent.tool_name == "control_media"
    assert intent.parameters["action"] == "play_pause"


def test_intent_control_media_next():
    intent = intent_classifier.classify_rule_based("skip this song")
    assert intent.intent == IntentType.CONTROL_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["action"] == "next"


def test_intent_control_media_volume_up():
    intent = intent_classifier.classify_rule_based("volume up")
    assert intent.intent == IntentType.CONTROL_MEDIA
    assert intent.tool_required is True
    assert intent.parameters["action"] == "volume_up"


def test_execute_control_media_tool():
    from backend.tools.media_player import control_windows_media
    with patch("backend.tools.media_player.press_windows_key", return_value=True):
        res = control_windows_media("play_pause")
        assert res["success"] is True
        assert "Toggled" in res["message"] or "Windows" in res["message"]

