import time
import uuid
from typing import List, Dict, Any, Optional

# In-memory store for incoming message notifications
_INCOMING_MESSAGES: List[Dict[str, Any]] = []

def add_incoming_message(
    sender: str,
    content: str,
    app_name: str = "WhatsApp",
    user_name: str = "Jamir"
) -> Dict[str, Any]:
    """Store an incoming message notification and generate speech announcement text."""
    msg_id = f"msg_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
    clean_sender = (sender or "Unknown Contact").strip().title()
    clean_content = (content or "").strip()
    clean_app = (app_name or "WhatsApp").strip()
    
    # Generate natural speech announcement
    speech_announcement = f"Hey {user_name}, you have a new {clean_app} message from {clean_sender}: '{clean_content}'."
    
    notification = {
        "id": msg_id,
        "sender": clean_sender,
        "content": clean_content,
        "app_name": clean_app,
        "timestamp": time.time(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_read": False,
        "speech_announcement": speech_announcement
    }
    
    _INCOMING_MESSAGES.insert(0, notification)
    # Keep last 50 messages
    if len(_INCOMING_MESSAGES) > 50:
        _INCOMING_MESSAGES.pop()
        
    return notification


def get_unread_messages() -> List[Dict[str, Any]]:
    """Retrieve all unread message notifications."""
    return [m for m in _INCOMING_MESSAGES if not m.get("is_read", False)]


def get_all_messages(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve recent incoming message notifications."""
    return _INCOMING_MESSAGES[:limit]


def mark_message_as_read(message_id: str) -> bool:
    """Mark a specific message notification as read."""
    for m in _INCOMING_MESSAGES:
        if m["id"] == message_id:
            m["is_read"] = True
            return True
    return False


def mark_all_as_read() -> int:
    """Mark all message notifications as read."""
    count = 0
    for m in _INCOMING_MESSAGES:
        if not m.get("is_read", False):
            m["is_read"] = True
            count += 1
    return count


def summarize_incoming_messages(user_name: str = "Jamir") -> Dict[str, Any]:
    """Generate a spoken summary of current unread or recent messages."""
    unread = get_unread_messages()
    if not unread:
        if not _INCOMING_MESSAGES:
            msg = f"{user_name}, you don't have any incoming WhatsApp messages right now."
        else:
            latest = _INCOMING_MESSAGES[0]
            msg = f"{user_name}, all your messages are caught up. Your last WhatsApp message was from {latest['sender']}: '{latest['content']}'."
        return {
            "has_unread": False,
            "count": 0,
            "spoken_summary": msg,
            "messages": _INCOMING_MESSAGES[:5]
        }
    
    count = len(unread)
    if count == 1:
        first = unread[0]
        spoken = f"{user_name}, you have 1 unread message from {first['sender']}: '{first['content']}'."
    else:
        senders = list({m['sender'] for m in unread[:3]})
        senders_str = ", ".join(senders)
        spoken = f"{user_name}, you have {count} unread messages from {senders_str}. The latest is from {unread[0]['sender']}: '{unread[0]['content']}'."
    
    return {
        "has_unread": True,
        "count": count,
        "spoken_summary": spoken,
        "messages": unread
    }
