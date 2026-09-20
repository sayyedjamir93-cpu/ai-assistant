from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User
from backend.api.auth import get_current_user
from backend.voice.text_to_speech import tts_engine
from backend.tools.whatsapp_announcer import (
    add_incoming_message,
    get_unread_messages,
    get_all_messages,
    mark_message_as_read,
    mark_all_as_read,
    summarize_incoming_messages
)

router = APIRouter(prefix="/messages", tags=["Messages & Notifications"])


class IncomingMessageRequest(BaseModel):
    sender: str = Field(..., min_length=1, json_schema_extra={"example": "Sakshi"})
    content: str = Field(..., min_length=1, json_schema_extra={"example": "Hey, are you free for the meeting?"})
    app_name: Optional[str] = Field("WhatsApp", json_schema_extra={"example": "WhatsApp"})


class MarkReadRequest(BaseModel):
    message_id: Optional[str] = None
    all: Optional[bool] = False


@router.get("/notifications")
def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Retrieve incoming message notifications."""
    if unread_only:
        msgs = get_unread_messages()
    else:
        msgs = get_all_messages(limit=30)
    return {
        "success": True,
        "unread_count": len(get_unread_messages()),
        "messages": msgs
    }


@router.post("/incoming")
def receive_incoming_message(
    payload: IncomingMessageRequest,
    synthesize_voice: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Ingest a new incoming message (e.g. from WhatsApp) and generate real-time voice speech announcement.
    """
    user_name = current_user.name or "Jamir"
    notif = add_incoming_message(
        sender=payload.sender,
        content=payload.content,
        app_name=payload.app_name or "WhatsApp",
        user_name=user_name
    )
    
    audio_base64 = None
    if synthesize_voice:
        try:
            synth = tts_engine.synthesize_to_bytes(notif["speech_announcement"])
            audio_base64 = synth.get("audio_base64")
        except Exception:
            audio_base64 = None

    return {
        "success": True,
        "notification": notif,
        "audio_base64": audio_base64,
        "spoken_text": notif["speech_announcement"]
    }


@router.post("/simulate")
def simulate_incoming_message(
    payload: Optional[IncomingMessageRequest] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Test helper: Simulates an incoming message from a contact to test SADIE's voice announcement.
    """
    default_sender = payload.sender if (payload and payload.sender) else "Sakshi"
    default_content = payload.content if (payload and payload.content) else "Hey, are you working on the Python project? Let me know when you're free!"
    default_app = payload.app_name if (payload and payload.app_name) else "WhatsApp"
    
    user_name = current_user.name or "Jamir"
    notif = add_incoming_message(
        sender=default_sender,
        content=default_content,
        app_name=default_app,
        user_name=user_name
    )
    
    audio_base64 = None
    try:
        synth = tts_engine.synthesize_to_bytes(notif["speech_announcement"])
        audio_base64 = synth.get("audio_base64")
    except Exception:
        audio_base64 = None

    return {
        "success": True,
        "simulated": True,
        "notification": notif,
        "audio_base64": audio_base64,
        "spoken_text": notif["speech_announcement"]
    }


@router.get("/read-aloud")
def read_messages_aloud(
    current_user: User = Depends(get_current_user)
):
    """
    Generate speech summary of current incoming messages.
    """
    user_name = current_user.name or "Jamir"
    summary = summarize_incoming_messages(user_name=user_name)
    
    audio_base64 = None
    try:
        synth = tts_engine.synthesize_to_bytes(summary["spoken_summary"])
        audio_base64 = synth.get("audio_base64")
    except Exception:
        audio_base64 = None

    return {
        "success": True,
        "summary": summary,
        "spoken_text": summary["spoken_summary"],
        "audio_base64": audio_base64
    }


@router.post("/mark-read")
def mark_read(
    payload: MarkReadRequest,
    current_user: User = Depends(get_current_user)
):
    """Mark message notification(s) as read."""
    if payload.all:
        count = mark_all_as_read()
        return {"success": True, "marked_read_count": count}
    elif payload.message_id:
        ok = mark_message_as_read(payload.message_id)
        return {"success": ok, "message_id": payload.message_id}
    return {"success": False, "error": "No message_id or all flag provided."}
