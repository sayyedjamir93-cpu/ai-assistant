import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db
from backend.ai.intent import intent_classifier, IntentType
from backend.tools.whatsapp_messenger import open_whatsapp_messenger

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
        "name": "Messaging Demo User",
        "email": "messaging@sadie.ai",
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Intent Detection Tests
# ==========================================

def test_intent_send_hii_to_sakshi():
    queries = [
        "sadie send hii to sakshi",
        "send hii to sakshi",
        "send a whatsapp message to sakshi saying hello",
        "message sakshi: how are you?",
        "whatsapp sakshi saying meeting at 5pm"
    ]
    for q in queries:
        res = intent_classifier.classify_rule_based(q)
        assert res.intent == IntentType.SEND_MESSAGE
        assert res.tool_required is True
        assert res.tool_name == "send_whatsapp"
        assert "sakshi" in res.parameters["contact_name"].lower()



# ==========================================
# 2. WhatsApp Tool Safe URL & Execution Tests
# ==========================================

def test_whatsapp_messenger_url_generation():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = open_whatsapp_messenger(contact_name="Sakshi", message="Hii", phone_number="+919876543210")
        assert res["success"] is True
        assert "whatsapp://send?phone=919876543210&text=Hii" in res["uri"]
        assert "wa.me/919876543210" in res["url"]
        assert "text=Hii" in res["url"]
        assert mock_start.called or mock_popen.called or mock_open.called


def test_whatsapp_messenger_without_phone():
    with patch("os.startfile") as mock_start, patch("subprocess.Popen") as mock_popen, patch("webbrowser.open") as mock_open:
        res = open_whatsapp_messenger(contact_name="Sakshi", message="Hello there!")
        assert res["success"] is True
        assert "whatsapp://send?text=Hello%20there%21" in res["uri"]
        assert "web.whatsapp.com/send?text=Hello%20there%21" in res["url"]
        assert mock_start.called or mock_popen.called or mock_open.called


# ==========================================
# 3. Contacts API & End-to-End Voice Pipeline
# ==========================================

def test_contacts_crud(client, auth_headers):
    # Create Contact
    create_res = client.post("/api/contacts", json={
        "name": "Sakshi",
        "phone_number": "+919876543210"
    }, headers=auth_headers)
    assert create_res.status_code == 201
    contact_id = create_res.json()["id"]

    # List Contacts
    list_res = client.get("/api/contacts", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["name"] == "Sakshi"

    # Delete Contact
    del_res = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)
    assert del_res.status_code == 200


def test_voice_pipeline_send_message_flow(client, auth_headers):
    # 1. Save contact for Sakshi
    client.post("/api/contacts", json={
        "name": "Sakshi",
        "phone_number": "+919876543210"
    }, headers=auth_headers)

    # 2. Send voice command: "Sadie send hii to sakshi"
    with patch("webbrowser.open"):
        voice_res = client.post("/api/voice/chat", json={
            "text_fallback": "Sadie send hii to sakshi",
            "mode": "normal",
            "synthesize_voice": True
        }, headers=auth_headers)
        assert voice_res.status_code == 200
        data = voice_res.json()
        assert data["intent"] == "SEND_MESSAGE"
        assert data["tool_executed"] == "send_whatsapp"
        assert "sakshi" in data["response_text"].lower()
        assert data["audio_base64"] is not None
