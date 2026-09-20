import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, Memory
from backend.api.auth import get_current_user

router = APIRouter(prefix="/memory", tags=["Controlled Memory"])


# ==========================================
# Pydantic Schemas
# ==========================================

class MemoryCreateRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "Python project location"})
    value: str = Field(..., min_length=1, json_schema_extra={"example": "Inside Projects/Python folder"})


class MemoryResponse(BaseModel):
    id: int
    user_id: int
    key: str
    value: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Memory Endpoints
# ==========================================

@router.get("", response_model=List[MemoryResponse])
def get_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View all stored personal memory items for the current user."""
    return db.query(Memory).filter(
        Memory.user_id == current_user.id
    ).order_by(Memory.created_at.desc()).all()


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def add_memory_item(
    payload: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Store an explicit memory item."""
    memory_item = Memory(
        user_id=current_user.id,
        key=payload.key.strip(),
        value=payload.value.strip()
    )
    db.add(memory_item)
    db.commit()
    db.refresh(memory_item)
    return memory_item


@router.delete("/{memory_id}")
def delete_memory_item(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific memory item."""
    memory_item = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    if not memory_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory item not found.")
    db.delete(memory_item)
    db.commit()
    return {"status": "success", "message": f"Memory item {memory_id} deleted."}


@router.delete("")
def clear_all_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all personal memories stored for the current user."""
    deleted_count = db.query(Memory).filter(Memory.user_id == current_user.id).delete()
    db.commit()
    return {"status": "success", "message": f"Cleared {deleted_count} memory items."}
