import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.database import get_db
from backend.database.models import User, StudySession, Task
from backend.api.auth import get_current_user

router = APIRouter(prefix="/study", tags=["Study Mode"])

# In-memory tracking for live session timers and pause states
_LIVE_STUDY_SESSIONS: Dict[int, Dict[str, Any]] = {}


# ==========================================
# Pydantic Schemas
# ==========================================

class StartStudySessionRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Python"})
    task_name: Optional[str] = Field(None, json_schema_extra={"example": "Recursion & Trees"})
    duration_minutes: Optional[int] = Field(25, ge=1, le=180, json_schema_extra={"example": 45})


class BreakSessionRequest(BaseModel):
    break_type: str = Field("short", json_schema_extra={"example": "short"})  # short (5m) | long (15m)
    duration_minutes: Optional[int] = Field(5, ge=1, le=60)


class StudySessionResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    task_name: Optional[str]
    duration_minutes: int
    completed: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentSessionStatus(BaseModel):
    is_active: bool
    session_id: Optional[int] = None
    subject: Optional[str] = None
    task_name: Optional[str] = None
    duration_minutes: Optional[int] = None
    started_at: Optional[str] = None
    ends_at: Optional[str] = None
    is_paused: bool = False
    is_break: bool = False
    message: str


class StudyAnalyticsResponse(BaseModel):
    total_study_minutes: int
    sessions_completed: int
    total_tasks_completed: int
    total_tasks_pending: int
    subject_breakdown: Dict[str, int]


# ==========================================
# Study Mode Endpoints
# ==========================================

@router.post("/start", response_model=CurrentSessionStatus)
def start_study_session(
    payload: StartStudySessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate Study Mode, record session in database, and start session timer."""
    duration = payload.duration_minutes or 25
    now = datetime.datetime.utcnow()
    ends = now + datetime.timedelta(minutes=duration)

    # Create DB record
    session_record = StudySession(
        user_id=current_user.id,
        subject=payload.subject.strip(),
        task_name=payload.task_name.strip() if payload.task_name else None,
        duration_minutes=duration,
        completed=False
    )
    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    # Also auto-create a task if task_name is given and doesn't exist
    if payload.task_name:
        existing_task = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.title == payload.task_name.strip()
        ).first()
        if not existing_task:
            db.add(Task(
                user_id=current_user.id,
                title=payload.task_name.strip(),
                description=f"Study task for {payload.subject}",
                completed=False
            ))
            db.commit()

    # Track in live state
    _LIVE_STUDY_SESSIONS[current_user.id] = {
        "session_id": session_record.id,
        "subject": payload.subject.strip(),
        "task_name": payload.task_name,
        "duration_minutes": duration,
        "started_at": now.isoformat(),
        "ends_at": ends.isoformat(),
        "is_paused": False,
        "is_break": False
    }

    return CurrentSessionStatus(
        is_active=True,
        session_id=session_record.id,
        subject=payload.subject.strip(),
        task_name=payload.task_name,
        duration_minutes=duration,
        started_at=now.isoformat(),
        ends_at=ends.isoformat(),
        is_paused=False,
        is_break=False,
        message=f"Study session started for '{payload.subject}' ({duration} minutes)."
    )


@router.get("/current", response_model=CurrentSessionStatus)
def get_current_study_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the current active study session status."""
    live = _LIVE_STUDY_SESSIONS.get(current_user.id)
    if not live:
        return CurrentSessionStatus(
            is_active=False,
            message="No active study session."
        )

    # Check if timer has elapsed
    now = datetime.datetime.utcnow()
    ends = datetime.datetime.fromisoformat(live["ends_at"])
    if now >= ends and not live["is_paused"]:
        return CurrentSessionStatus(
            is_active=True,
            session_id=live["session_id"],
            subject=live["subject"],
            task_name=live["task_name"],
            duration_minutes=live["duration_minutes"],
            started_at=live["started_at"],
            ends_at=live["ends_at"],
            is_paused=False,
            is_break=live.get("is_break", False),
            message="Study session timer finished! Time for a well-deserved break."
        )

    return CurrentSessionStatus(
        is_active=True,
        session_id=live["session_id"],
        subject=live["subject"],
        task_name=live["task_name"],
        duration_minutes=live["duration_minutes"],
        started_at=live["started_at"],
        ends_at=live["ends_at"],
        is_paused=live["is_paused"],
        is_break=live.get("is_break", False),
        message=f"Focusing on {live['subject']}."
    )


@router.post("/pause", response_model=CurrentSessionStatus)
def pause_study_session(
    current_user: User = Depends(get_current_user)
):
    """Pause the current active study session timer."""
    live = _LIVE_STUDY_SESSIONS.get(current_user.id)
    if not live:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active study session to pause.")
    live["is_paused"] = True
    return CurrentSessionStatus(
        is_active=True,
        session_id=live["session_id"],
        subject=live["subject"],
        task_name=live["task_name"],
        duration_minutes=live["duration_minutes"],
        started_at=live["started_at"],
        ends_at=live["ends_at"],
        is_paused=True,
        message=f"Study session for '{live['subject']}' paused."
    )


@router.post("/resume", response_model=CurrentSessionStatus)
def resume_study_session(
    current_user: User = Depends(get_current_user)
):
    """Resume a paused study session."""
    live = _LIVE_STUDY_SESSIONS.get(current_user.id)
    if not live:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No study session to resume.")
    live["is_paused"] = False
    return CurrentSessionStatus(
        is_active=True,
        session_id=live["session_id"],
        subject=live["subject"],
        task_name=live["task_name"],
        duration_minutes=live["duration_minutes"],
        started_at=live["started_at"],
        ends_at=live["ends_at"],
        is_paused=False,
        message=f"Study session resumed."
    )


@router.post("/complete")
def complete_study_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete and conclude the current study session."""
    live = _LIVE_STUDY_SESSIONS.pop(current_user.id, None)
    if live and live.get("session_id"):
        session_rec = db.query(StudySession).filter(
            StudySession.id == live["session_id"],
            StudySession.user_id == current_user.id
        ).first()
        if session_rec:
            session_rec.completed = True
            db.commit()

    return {
        "status": "success",
        "message": "Study session successfully completed and recorded!"
    }


@router.post("/break", response_model=CurrentSessionStatus)
def start_break_session(
    payload: BreakSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a short (5m) or long (15m) rest break."""
    mins = 5 if payload.break_type == "short" else 15
    if payload.duration_minutes:
        mins = payload.duration_minutes
    now = datetime.datetime.utcnow()
    ends = now + datetime.timedelta(minutes=mins)

    _LIVE_STUDY_SESSIONS[current_user.id] = {
        "session_id": None,
        "subject": "Rest Break",
        "task_name": f"{payload.break_type.title()} Break",
        "duration_minutes": mins,
        "started_at": now.isoformat(),
        "ends_at": ends.isoformat(),
        "is_paused": False,
        "is_break": True
    }

    return CurrentSessionStatus(
        is_active=True,
        subject="Rest Break",
        task_name=f"{payload.break_type.title()} Break",
        duration_minutes=mins,
        started_at=now.isoformat(),
        ends_at=ends.isoformat(),
        is_paused=False,
        is_break=True,
        message=f"{payload.break_type.title()} break started ({mins} minutes). Relax and recharge!"
    )


@router.get("/analytics", response_model=StudyAnalyticsResponse)
def get_study_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate productivity analytics: total minutes studied, completed sessions, and task progress."""
    sessions = db.query(StudySession).filter(StudySession.user_id == current_user.id).all()
    completed_sessions = [s for s in sessions if s.completed]
    total_minutes = sum(s.duration_minutes for s in completed_sessions)

    # Subject breakdown
    subject_counts: Dict[str, int] = {}
    for s in sessions:
        subject_counts[s.subject] = subject_counts.get(s.subject, 0) + s.duration_minutes

    # Tasks
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    tasks_done = len([t for t in tasks if t.completed])
    tasks_pending = len([t for t in tasks if not t.completed])

    return StudyAnalyticsResponse(
        total_study_minutes=total_minutes,
        sessions_completed=len(completed_sessions),
        total_tasks_completed=tasks_done,
        total_tasks_pending=tasks_pending,
        subject_breakdown=subject_counts
    )


@router.get("/history", response_model=List[StudySessionResponse])
def get_study_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve past study sessions log."""
    return db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).order_by(StudySession.created_at.desc()).all()
