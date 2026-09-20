import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.tools.whatsapp_announcer import (
    add_incoming_message,
    get_unread_messages,
    get_all_messages,
    mark_message_as_read,
    mark_all_as_read,
    summarize_incoming_messages,
    _INCOMING_MESSAGES
)
from backend.ai.intent import intent_classifier, IntentType


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    register_payload = {
        "name": "Jamir",
        "email": "jamir.announcer@sadie.ai",
        "password": "Password123!"
    }
    client.post("/api/auth/register", json=register_payload)
    login_res = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# 1. Announcer Unit Tests
# ==========================================

def test_add_incoming_message_and_speech():
    _INCOMING_MESSAGES.clear()
    notif = add_incoming_message(sender="Sakshi", content="Are you free for coffee?", app_name="WhatsApp", user_name="Jamir")
    assert notif["sender"] == "Sakshi"
    assert notif["content"] == "Are you free for coffee?"
    assert notif["app_name"] == "WhatsApp"
    assert notif["is_read"] is False
    assert "Hey Jamir, you have a new WhatsApp message from Sakshi: 'Are you free for coffee?'." in notif["speech_announcement"]


def test_unread_and_mark_read():
    _INCOMING_MESSAGES.clear()
    msg1 = add_incoming_message(sender="Alex", content="Meeting in 10 mins", user_name="Jamir")
    msg2 = add_incoming_message(sender="Sakshi", content="Got the files", user_name="Jamir")
    
    assert len(get_unread_messages()) == 2
    assert mark_message_as_read(msg1["id"]) is True
    assert len(get_unread_messages()) == 1
    
    assert mark_all_as_read() == 1
    assert len(get_unread_messages()) == 0


def test_summarize_incoming_messages():
    _INCOMING_MESSAGES.clear()
    res_empty = summarize_incoming_messages(user_name="Jamir")
    assert res_empty["has_unread"] is False
    assert "don't have any incoming WhatsApp messages" in res_empty["spoken_summary"]

    add_incoming_message(sender="Sakshi", content="Call me when free", user_name="Jamir")
    res_unread = summarize_incoming_messages(user_name="Jamir")
    assert res_unread["has_unread"] is True
    assert res_unread["count"] == 1
    assert "1 unread message from Sakshi: 'Call me when free'." in res_unread["spoken_summary"]


# ==========================================
# 2. Intent Classifier Tests
# ==========================================

def test_intent_read_whatsapp_messages():
    queries = [
        "read my whatsapp messages",
        "check my whatsapp messages",
        "who messaged me on whatsapp",
        "do i have any new messages",
        "read latest message",
        "who sent me a message",
        "any new messages"
    ]
    for q in queries:
        res = intent_classifier.classify_rule_based(q)
        assert res is not None, f"Failed match for query: {q}"
        assert res.intent == IntentType.READ_MESSAGES, f"Failed intent for query: {q}"
        assert res.tool_required is True
        assert res.tool_name == "read_messages"


# ==========================================
# 3. API Endpoints Tests
# ==========================================

def test_simulate_incoming_message_api(client, auth_headers):
    with patch("backend.voice.text_to_speech.tts_engine.synthesize_to_bytes", return_value={"success": True, "audio_base64": "fake_audio_base64"}):
        res = client.post(
            "/api/messages/simulate",
            json={"sender": "Sakshi", "content": "Project files submitted!"},
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["notification"]["sender"] == "Sakshi"
        assert "Project files submitted!" in data["spoken_text"]
        assert data["audio_base64"] == "fake_audio_base64"


def test_get_notifications_api(client, auth_headers):
    res = client.get("/api/messages/notifications", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "messages" in data


def test_read_aloud_api(client, auth_headers):
    with patch("backend.voice.text_to_speech.tts_engine.synthesize_to_bytes", return_value={"success": True, "audio_base64": "fake_audio_base64"}):
        res = client.get("/api/messages/read-aloud", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["audio_base64"] == "fake_audio_base64"


def test_assistant_chat_read_messages_flow(client, auth_headers):
    _INCOMING_MESSAGES.clear()
    add_incoming_message(sender="Sakshi", content="Hey Jamir, dinner at 8pm?", user_name="Jamir")
    
    res = client.post(
        "/api/assistant/chat",
        json={"message": "Sadie, read my WhatsApp messages"},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "READ_MESSAGES"
    assert data["tool_required"] is True
    assert "Sakshi" in data["message"]
    assert "dinner at 8pm?" in data["message"]
