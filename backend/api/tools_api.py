from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User, ToolPermission
from backend.api.auth import get_current_user
from backend.ai.tool_router import tool_router, TOOL_REGISTRY
from backend.tools.system_info import get_safe_system_info
from backend.tools.timer import get_active_timers

router = APIRouter(prefix="/tools", tags=["Tools"])


# ==========================================
# Pydantic Schemas
# ==========================================

class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., json_schema_extra={"example": "open_application"})
    parameters: Dict[str, Any] = Field(default_factory=dict, json_schema_extra={"example": {"app_name": "calc.exe"}})


class PermissionUpdateRequest(BaseModel):
    is_allowed: bool = Field(..., json_schema_extra={"example": True})


# ==========================================
# Tools Endpoints
# ==========================================

@router.get("", response_model=List[Dict[str, Any]])
def list_tools():
    """Retrieve all available desktop tools and their parameter schemas."""
    return tool_router.list_available_tools()


@router.post("/execute")
def execute_tool_endpoint(
    payload: ToolExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a tool within security guardrails and permission checks."""
    result = tool_router.execute(
        tool_name=payload.tool_name,
        parameters=payload.parameters,
        user=current_user,
        db=db
    )
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Tool execution failed.")
        )
    return result


@router.get("/permissions")
def get_user_tool_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's tool permission status list."""
    permissions = db.query(ToolPermission).filter(ToolPermission.user_id == current_user.id).all()
    perm_dict = {p.tool_name: p.is_allowed for p in permissions}
    
    # Merge with registry defaults
    all_perms = []
    for tool_name, tool_data in TOOL_REGISTRY.items():
        is_allowed = perm_dict.get(tool_name, True)
        all_perms.append({
            "tool_name": tool_name,
            "display_name": tool_data["display_name"],
            "requires_permission": tool_data["requires_permission"],
            "is_allowed": is_allowed
        })
    return all_perms


@router.put("/permissions/{tool_name}")
def update_user_tool_permission(
    tool_name: str,
    payload: PermissionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable or disable permission for a specific tool in User Settings."""
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found."
        )

    perm = db.query(ToolPermission).filter(
        ToolPermission.user_id == current_user.id,
        ToolPermission.tool_name == tool_name
    ).first()

    if not perm:
        perm = ToolPermission(
            user_id=current_user.id,
            tool_name=tool_name,
            is_allowed=payload.is_allowed
        )
        db.add(perm)
    else:
        perm.is_allowed = payload.is_allowed

    db.commit()
    return {
        "status": "success",
        "tool_name": tool_name,
        "is_allowed": payload.is_allowed,
        "message": f"Permission for '{tool_name}' set to {payload.is_allowed}."
    }


@router.get("/timers")
def get_timers():
    """Retrieve all currently active countdown timers."""
    return get_active_timers()


# Standalone system info router
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/info")
def get_system_info_endpoint():
    """Retrieve read-only hardware, CPU, RAM, storage, and runtime metrics."""
    return get_safe_system_info()
