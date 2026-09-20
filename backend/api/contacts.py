import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, Contact
from backend.api.auth import get_current_user
from backend.tools.whatsapp_messenger import open_whatsapp_messenger

router = APIRouter(prefix="/contacts", tags=["Contacts & Messaging"])


# ==========================================
# Pydantic Schemas
# ==========================================

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Sakshi"})
    phone_number: Optional[str] = Field(None, max_length=50, json_schema_extra={"example": "+919876543210"})


class ContactResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone_number: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    contact_name: str = Field(..., json_schema_extra={"example": "Sakshi"})
    message: str = Field(..., json_schema_extra={"example": "Hii"})
    phone_number: Optional[str] = Field(None, json_schema_extra={"example": "+919876543210"})



# ==========================================
# Endpoints
# ==========================================

@router.get("", response_model=List[ContactResponse])
def get_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all contacts saved for the current user."""
    return db.query(Contact).filter(Contact.user_id == current_user.id).order_by(Contact.name.asc()).all()


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new contact with phone number for fast WhatsApp messaging."""
    existing = db.query(Contact).filter(
        Contact.user_id == current_user.id,
        Contact.name.ilike(payload.name.strip())
    ).first()

    if existing:
        existing.phone_number = payload.phone_number.strip() if payload.phone_number else existing.phone_number
        db.commit()
        db.refresh(existing)
        return existing

    new_contact = Contact(
        user_id=current_user.id,
        name=payload.name.strip(),
        phone_number=payload.phone_number.strip() if payload.phone_number else None
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.delete("/{contact_id}", status_code=status.HTTP_200_OK)
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contact by ID."""
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully", "contact_id": contact_id}


@router.post("/send-message", status_code=status.HTTP_200_OK)
def send_message_endpoint(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger WhatsApp message launcher directly."""
    phone = payload.phone_number
    if not phone:
        contact = db.query(Contact).filter(
            Contact.user_id == current_user.id,
            Contact.name.ilike(f"%{payload.contact_name.strip()}%")
        ).first()
        if contact and contact.phone_number:
            phone = contact.phone_number

    res = open_whatsapp_messenger(
        contact_name=payload.contact_name,
        message=payload.message,
        phone_number=phone
    )
    return res
