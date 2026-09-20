import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, Reminder
from backend.api.auth import get_current_user

router = APIRouter(prefix="/reminders", tags=["Reminders"])


# ==========================================
# Pydantic Schemas
# ==========================================

class ReminderCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "Submit assignment at 7 PM"})
    remind_at: datetime.datetime = Field(..., json_schema_extra={"example": "2026-09-02T19:00:00"})


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    remind_at: datetime.datetime
    is_triggered: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Reminders Endpoints
# ==========================================

@router.get("", response_model=List[ReminderResponse])
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all reminders for current user."""
    return db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).order_by(Reminder.remind_at.asc()).all()


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reminder."""
    reminder = Reminder(
        user_id=current_user.id,
        title=payload.title.strip(),
        remind_at=payload.remind_at,
        is_triggered=False
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a reminder."""
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found.")
    db.delete(reminder)
    db.commit()
    return {"status": "success", "message": f"Reminder {reminder_id} deleted."}
