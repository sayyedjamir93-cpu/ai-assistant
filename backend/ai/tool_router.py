import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import User, ToolPermission, Contact
from backend.tools.app_launcher import launch_application
from backend.tools.folder_launcher import launch_folder
from backend.tools.web_search import search_web
from backend.tools.timer import start_countdown_timer, get_active_timers
from backend.tools.system_info import get_safe_system_info
from backend.tools.whatsapp_messenger import open_whatsapp_messenger
from backend.tools.media_player import play_media, control_windows_media
from backend.tools.vscode_creator import create_and_open_in_vscode
from backend.tools.whatsapp_announcer import summarize_incoming_messages



TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "play_media": {
        "name": "play_media",
        "display_name": "Media Player (YouTube & Spotify)",
        "description": "Plays songs, music tracks, videos, and tutorials on YouTube or Spotify based on user demand.",
        "parameters_schema": {
            "platform": {"type": "string", "description": "Target platform: 'youtube' or 'spotify'", "required": True},
            "query": {"type": "string", "description": "Song name, artist, video title, or search query", "required": False}
        },
        "requires_permission": False
    },
    "open_application": {
        "name": "open_application",
        "display_name": "Open Application",
        "description": "Safely launches allowlisted desktop applications such as Calculator, Notepad, VS Code, or Chrome.",
        "parameters_schema": {
            "app_name": {"type": "string", "description": "Name or executable of the application to open", "required": True}
        },
        "requires_permission": False
    },
    "open_folder": {
        "name": "open_folder",
        "display_name": "Open Folder",
        "description": "Safely opens allowlisted directories such as Documents, Downloads, Projects, or Study Materials in File Explorer.",
        "parameters_schema": {
            "folder_name": {"type": "string", "description": "Target folder name to explore", "required": True}
        },
        "requires_permission": False
    },
    "web_search": {
        "name": "web_search",
        "display_name": "Web Search",
        "description": "Performs a safe internet search to retrieve sources, headlines, and summaries.",
        "parameters_schema": {
            "query": {"type": "string", "description": "Search keyword or question", "required": True}
        },
        "requires_permission": False
    },
    "start_timer": {
        "name": "start_timer",
        "display_name": "Start Timer",
        "description": "Starts a countdown timer for study or tasks.",
        "parameters_schema": {
            "duration_minutes": {"type": "number", "description": "Timer duration in minutes", "required": True},
            "label": {"type": "string", "description": "Optional label for the timer", "required": False}
        },
        "requires_permission": False
    },
    "system_info": {
        "name": "system_info",
        "display_name": "System Information",
        "description": "Retrieves read-only hardware, CPU, RAM, storage, and OS diagnostics.",
        "parameters_schema": {},
        "requires_permission": False
    },
    "datetime": {
        "name": "datetime",
        "display_name": "Current Date & Time",
        "description": "Retrieves the current date, time, and timezone.",
        "parameters_schema": {},
        "requires_permission": False
    },
    "send_whatsapp": {
        "name": "send_whatsapp",
        "display_name": "WhatsApp Messenger",
        "description": "Safely opens WhatsApp with pre-filled message for target contact.",
        "parameters_schema": {
            "contact_name": {"type": "string", "description": "Target contact name", "required": True},
            "message": {"type": "string", "description": "Message content to send", "required": True},
            "phone_number": {"type": "string", "description": "Optional phone number", "required": False}
        },
        "requires_permission": False
    },
    "control_media": {
        "name": "control_media",
        "display_name": "Windows Media & Volume Controller",
        "description": "Natively controls Windows media playback (Play/Pause, Next, Prev) and system volume without browser dependency.",
        "parameters_schema": {
            "action": {"type": "string", "description": "Action: play_pause, next, previous, volume_up, volume_down, mute", "required": True}
        },
        "requires_permission": False
    },
    "read_messages": {
        "name": "read_messages",
        "display_name": "WhatsApp & Messages Voice Reader",
        "description": "Reads and summarizes incoming WhatsApp and messaging notifications out loud with speech.",
        "parameters_schema": {},
        "requires_permission": False
    },
    "create_code_file": {
        "name": "create_code_file",
        "display_name": "VS Code Program & Project Generator",
        "description": "Creates production-ready code files in any language and launches them directly in Visual Studio Code on Windows.",
        "parameters_schema": {
            "language": {"type": "string", "description": "Programming language (python, cpp, c, java, javascript, html, rust, go, etc.)", "required": True},
            "task_description": {"type": "string", "description": "What the program should do (e.g. sum of two numbers, calculator, fibonacci)", "required": True},
            "filename": {"type": "string", "description": "Optional custom filename", "required": False},
            "open_editor": {"type": "boolean", "description": "Whether to open in VS Code (default true)", "required": False}
        },
        "requires_permission": False
    }
}



class ToolRouter:
    """Security gatekeeper and dispatcher for all SADIE tool invocations."""

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """Return metadata for all registered tools."""
        return list(TOOL_REGISTRY.values())

    def check_permission(self, tool_name: str, user: Optional[User] = None, db: Optional[Session] = None) -> bool:
        """Verify if the tool is permitted for the specified user."""
        tool_meta = TOOL_REGISTRY.get(tool_name)
        if not tool_meta:
            return False

        if db and user:
            perm = db.query(ToolPermission).filter(
                ToolPermission.user_id == user.id,
                ToolPermission.tool_name == tool_name
            ).first()
            if perm is not None and not perm.is_allowed:
                return False

        return True

    def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Execute a tool with parameter validation and permission enforcement."""
        TOOL_ALIASES = {
            "open_app": "open_application",
            "open_folder": "open_folder",
            "open_dir": "open_folder",
            "create_program": "create_code_file",
            "create_code": "create_code_file",
            "check_messages": "read_messages",
            "read_whatsapp": "read_messages"
        }
        canonical_tool_name = TOOL_ALIASES.get(tool_name, tool_name)

        if canonical_tool_name not in TOOL_REGISTRY:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": f"Unknown tool: '{tool_name}'. Available tools: {list(TOOL_REGISTRY.keys())}"
            }

        # Permission Check
        if not self.check_permission(canonical_tool_name, user, db):
            return {
                "success": False,
                "tool_name": canonical_tool_name,
                "error": f"Permission Denied: User has disabled permission for '{canonical_tool_name}' in Settings."
            }

        # Safe Dispatch
        try:
            if canonical_tool_name == "open_application":
                app_name = parameters.get("app_name") or parameters.get("display_name", "")
                query = parameters.get("query")
                res = launch_application(app_name=app_name, query=query)
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res, "message": res.get("message")}

            elif canonical_tool_name == "open_folder":
                folder_name = parameters.get("folder_name", "")
                res = launch_folder(folder_name=folder_name)
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res}

            elif tool_name == "web_search":
                query = parameters.get("query", "")
                res = search_web(query=query)
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res}

            elif tool_name == "start_timer":
                mins = float(parameters.get("duration_minutes", 25))
                label = parameters.get("label")
                res = start_countdown_timer(duration_minutes=mins, label=label)
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res}

            elif tool_name == "system_info":
                res = get_safe_system_info()
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res}

            elif tool_name == "datetime":
                now = datetime.datetime.now()
                res = {
                    "current_date": now.strftime("%A, %B %d, %Y"),
                    "current_time": now.strftime("%I:%M:%S %p"),
                    "iso": now.isoformat()
                }
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": res,
                    "message": f"Today is {res['current_date']}, and the time is {res['current_time']}."
                }

            elif tool_name == "send_whatsapp":
                contact_name = parameters.get("contact_name", "Contact")
                msg = parameters.get("message", "Hi")
                phone = parameters.get("phone_number")

                # If phone is not provided and db session available, search contacts
                if not phone and db and user:
                    matched_contact = db.query(Contact).filter(
                        Contact.user_id == user.id,
                        Contact.name.ilike(f"%{contact_name}%")
                    ).first()
                    if matched_contact and matched_contact.phone_number:
                        phone = matched_contact.phone_number

                res = open_whatsapp_messenger(contact_name=contact_name, message=msg, phone_number=phone)
                return {"success": res.get("success", False), "tool_name": tool_name, "result": res, "message": res.get("status_message", "WhatsApp launched.")}

            elif tool_name == "play_media":
                platform = parameters.get("platform", "youtube")
                query = parameters.get("query", "")
                media_type = parameters.get("media_type", "media")
                res = play_media(platform=platform, query=query, media_type=media_type)
                return {
                    "success": res.get("success", False),
                    "tool_name": tool_name,
                    "result": res,
                    "message": res.get("message", f"Opened {platform.title()}.")
                }

            elif tool_name == "control_media":
                action = parameters.get("action", "play_pause")
                res = control_windows_media(action=action)
                return {
                    "success": res.get("success", False),
                    "tool_name": tool_name,
                    "result": res,
                    "message": res.get("message", "Executed Windows media control.")
                }

            elif tool_name == "create_code_file":
                lang = parameters.get("language", "python")
                task_desc = parameters.get("task_description", "sum of two numbers")
                fname = parameters.get("filename")
                open_ed = parameters.get("open_editor", True)
                res = create_and_open_in_vscode(
                    language=lang,
                    task_description=task_desc,
                    filename=fname,
                    open_editor=open_ed
                )
                return {
                    "success": res.get("success", False),
                    "tool_name": tool_name,
                    "result": res,
                    "message": res.get("message", f"Created {lang.upper()} program in VS Code.")
                }

            elif canonical_tool_name == "read_messages":
                user_name = user.name if user else "Jamir"
                summary = summarize_incoming_messages(user_name=user_name)
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": summary,
                    "message": summary["spoken_summary"]
                }

            return {

                "success": False,
                "tool_name": tool_name,
                "error": f"Tool '{tool_name}' handler not implemented."
            }

        except Exception as e:
            return {
                "success": False,
                "tool_name": tool_name,
                "error": f"Error executing tool '{tool_name}': {str(e)}"
            }


tool_router = ToolRouter()
