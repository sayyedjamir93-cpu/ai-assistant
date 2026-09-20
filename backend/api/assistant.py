import json
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, Conversation, Message, Memory
from backend.api.auth import get_current_user
from backend.ai.brain import brain
from backend.ai.tool_router import tool_router

router = APIRouter(prefix="/assistant", tags=["Assistant"])


# ==========================================
# Pydantic Schemas
# ==========================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, json_schema_extra={"example": "Hey Sadie, explain Python recursion."})
    conversation_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    mode: Optional[str] = Field("normal", json_schema_extra={"example": "normal"})  # normal | study | coding


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    intent: str
    tool_required: bool
    tool_name: Optional[str] = None
    tool_parameters: Dict[str, Any] = Field(default_factory=dict)
    tool_result: Optional[Dict[str, Any]] = None
    mode: str
    source: str


class MessageItem(BaseModel):
    id: int
    sender: str
    content: str
    tool_calls: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetail(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    messages: List[MessageItem] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Assistant & Chat Endpoints
# ==========================================

@router.post("/chat", response_model=ChatResponse)
def assistant_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process user natural language message, maintain conversation history, detect intents, and return responses."""
    # 1. Retrieve or create conversation
    conversation = None
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == payload.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )
    else:
        title_summary = payload.message.strip()[:40] + ("..." if len(payload.message.strip()) > 40 else "")
        conversation = Conversation(
            user_id=current_user.id,
            title=title_summary
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Fetch recent conversation history
    past_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).limit(10).all()

    formatted_history = [
        {"sender": m.sender, "content": m.content}
        for m in past_messages
    ]

    # 3. Fetch user memories
    user_memories_records = db.query(Memory).filter(Memory.user_id == current_user.id).all()
    user_memories = [{"key": m.key, "value": m.value} for m in user_memories_records]

    # 4. Invoke AI Brain
    brain_result = brain.process_message(
        user_message=payload.message,
        conversation_history=formatted_history,
        mode=payload.mode or "normal",
        memories=user_memories
    )

    # 4.5 Execute Tool if required
    tool_executed = None
    tool_result = None
    if brain_result["tool_required"] and brain_result.get("tool_name"):
        tool_name = brain_result["tool_name"]
        tool_params = brain_result.get("tool_parameters", {})
        exec_res = tool_router.execute(
            tool_name=tool_name,
            parameters=tool_params,
            user=current_user,
            db=db
        )
        tool_executed = tool_name
        tool_result = exec_res

        # If tool returned a friendly completion message, use it as response
        if exec_res.get("success"):
            if "message" in exec_res.get("result", {}):
                brain_result["response_text"] = exec_res["result"]["message"]
            elif "message" in exec_res:
                brain_result["response_text"] = exec_res["message"]
        elif not exec_res.get("success") and exec_res.get("error"):
            brain_result["response_text"] = f"I tried to {tool_name}, but encountered an issue: {exec_res.get('error')}"

    # 5. Persist User Message
    user_msg_record = Message(
        conversation_id=conversation.id,
        sender="user",
        content=payload.message.strip()
    )
    db.add(user_msg_record)

    # 6. Persist Sadie Response Message
    tool_calls_json = None
    if brain_result["tool_required"]:
        tool_calls_json = json.dumps({
            "tool_name": brain_result["tool_name"],
            "parameters": brain_result["tool_parameters"],
            "result": tool_result
        })

    sadie_msg_record = Message(
        conversation_id=conversation.id,
        sender="sadie",
        content=brain_result["response_text"],
        tool_calls=tool_calls_json
    )
    db.add(sadie_msg_record)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=brain_result["response_text"],
        intent=brain_result["intent"],
        tool_required=brain_result["tool_required"],
        tool_name=brain_result["tool_name"],
        tool_parameters=brain_result["tool_parameters"],
        tool_result=tool_result,
        mode=brain_result["mode"],
        source=brain_result["source"]
    )


@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all conversations for the current authenticated user."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full message history for a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    db.delete(conversation)
    db.commit()
    return {"status": "success", "message": f"Conversation {conversation_id} deleted."}
