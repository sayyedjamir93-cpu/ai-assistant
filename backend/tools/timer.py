import time
import datetime
from typing import Dict, Any, Optional

# In-memory active timer tracking
_ACTIVE_TIMERS: Dict[str, Dict[str, Any]] = {}


def start_countdown_timer(duration_minutes: float, label: Optional[str] = None) -> Dict[str, Any]:
    """Calculate and initialize a countdown timer."""
    if duration_minutes <= 0:
        return {
            "success": False,
            "error": "Timer duration must be greater than 0 minutes."
        }

    now = datetime.datetime.utcnow()
    duration_seconds = int(duration_minutes * 60)
    end_time = now + datetime.timedelta(seconds=duration_seconds)
    timer_id = f"timer_{int(time.time())}"
    timer_label = label or f"{duration_minutes} min timer"

    timer_data = {
        "timer_id": timer_id,
        "label": timer_label,
        "duration_minutes": duration_minutes,
        "duration_seconds": duration_seconds,
        "started_at": now.isoformat(),
        "ends_at": end_time.isoformat(),
        "is_active": True
    }
    _ACTIVE_TIMERS[timer_id] = timer_data

    return {
        "success": True,
        "timer": timer_data,
        "message": f"Started {duration_minutes}-minute timer: '{timer_label}'."
    }


def get_active_timers() -> Dict[str, Any]:
    """Retrieve all currently active timers."""
    now = datetime.datetime.utcnow()
    # Update active status
    for t in _ACTIVE_TIMERS.values():
        ends = datetime.datetime.fromisoformat(t["ends_at"])
        if now >= ends:
            t["is_active"] = False

    return {
        "success": True,
        "timers": list(_ACTIVE_TIMERS.values())
    }
