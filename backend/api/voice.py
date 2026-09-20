import json
import base64
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, Conversation, Message
from backend.api.auth import get_current_user
from backend.voice.speech_to_text import stt_engine
from backend.voice.text_to_speech import tts_engine
from backend.ai.brain import brain
from backend.ai.tool_router import tool_router

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])


# ==========================================
# Pydantic Schemas
# ==========================================

class TranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio data")
    language: Optional[str] = "en-US"


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, json_schema_extra={"example": "Calculator is open."})
    language: Optional[str] = "en"


class VoiceChatRequest(BaseModel):
    audio_base64: Optional[str] = Field(None, description="Base64 audio if sending audio directly")
    text_fallback: Optional[str] = Field(None, description="Direct text if client already transcribed speech")
    conversation_id: Optional[int] = None
    mode: Optional[str] = "normal"
    synthesize_voice: Optional[bool] = True


class VoiceChatResponse(BaseModel):
    transcribed_text: str
    conversation_id: int
    response_text: str
    intent: str
    tool_executed: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    audio_base64: Optional[str] = None
    mode: str


# ==========================================
# Voice Endpoints
# ==========================================

@router.post("/transcribe")
def transcribe_audio(payload: TranscribeRequest):
    """Transcribe base64 audio payload into text using Speech-to-Text."""
    result = stt_engine.transcribe_base64(payload.audio_base64, language=payload.language or "en-US")
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Speech recognition failed.")
        )
    return result


@router.post("/transcribe-file")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: str = Form("en-US")
):
    """Transcribe an uploaded audio file (WAV/MP3/WebM)."""
    audio_bytes = await file.read()
    result = stt_engine.transcribe_audio_bytes(audio_bytes, language=language)
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Speech recognition failed.")
        )
    return result


@router.post("/synthesize")
def synthesize_speech(payload: SynthesizeRequest):
    """Convert text into synthesized speech audio (base64 MP3)."""
    result = tts_engine.synthesize_to_bytes(payload.text, language=payload.language)
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Text-to-Speech synthesis failed.")
        )
    return result


@router.post("/chat", response_model=VoiceChatResponse)
def voice_chat_pipeline(
    payload: VoiceChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Full Voice Assistant Pipeline: Voice -> STT -> Brain -> Tool -> Response -> TTS."""
    # 1. Speech-to-Text
    user_query = ""
    if payload.audio_base64:
        stt_res = stt_engine.transcribe_base64(payload.audio_base64)
        if stt_res.get("success", False):
            user_query = stt_res.get("text", "").strip()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stt_res.get("error", "Could not transcribe user voice.")
            )
    elif payload.text_fallback:
        user_query = payload.text_fallback.strip()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either audio_base64 or text_fallback must be provided."
        )

    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No speech or text detected."
        )

    # 2. Retrieve or Create Conversation
    conversation = None
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == payload.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conversation:
        title = user_query[:40] + ("..." if len(user_query) > 40 else "")
        conversation = Conversation(user_id=current_user.id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 3. Fetch past messages & memories
    past_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).limit(8).all()
    history = [{"sender": m.sender, "content": m.content} for m in past_messages]

    # 4. Invoke AI Brain
    brain_result = brain.process_message(
        user_message=user_query,
        conversation_history=history,
        mode=payload.mode or "normal"
    )

    response_text = brain_result["response_text"]
    tool_executed = None
    tool_result = None

    # 5. Execute Tool if required
    if brain_result["tool_required"] and brain_result["tool_name"]:
        tool_name = brain_result["tool_name"]
        tool_params = brain_result["tool_parameters"]
        exec_res = tool_router.execute(
            tool_name=tool_name,
            parameters=tool_params,
            user=current_user,
            db=db
        )
        tool_executed = tool_name
        tool_result = exec_res

        # If tool returned a friendly completion message, use it for speech
        if exec_res.get("success") and "message" in exec_res.get("result", {}):
            response_text = exec_res["result"]["message"]
        elif not exec_res.get("success"):
            response_text = f"I tried to {tool_name}, but encountered an issue: {exec_res.get('error')}"

    # 6. Save Messages in Database
    db.add(Message(conversation_id=conversation.id, sender="user", content=user_query))
    db.add(Message(
        conversation_id=conversation.id,
        sender="sadie",
        content=response_text,
        tool_calls=json.dumps({"tool": tool_executed, "result": tool_result}) if tool_executed else None
    ))
    db.commit()

    # 7. Synthesize Speech (TTS)
    audio_base64 = None
    if payload.synthesize_voice:
        tts_res = tts_engine.synthesize_to_bytes(response_text)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")

    return VoiceChatResponse(
        transcribed_text=user_query,
        conversation_id=conversation.id,
        response_text=response_text,
        intent=brain_result["intent"],
        tool_executed=tool_executed,
        tool_result=tool_result,
        audio_base64=audio_base64,
        mode=payload.mode or "normal"
    )
