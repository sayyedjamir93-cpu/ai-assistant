import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from backend.config import settings, PROJECT_ROOT


def get_canonical_folder_path(folder_name: str) -> Path:
    """Map friendly folder names to resolved safe system paths."""
    home = Path.home()
    folder_key = folder_name.lower().strip()

    folder_map = {
        "documents": home / "Documents",
        "downloads": home / "Downloads",
        "desktop": home / "Desktop",
        "pictures": home / "Pictures",
        "music": home / "Music",
        "videos": home / "Videos",
        "projects": home / "Projects",
        "python project": PROJECT_ROOT,
        "python folder": PROJECT_ROOT,
        "study materials": PROJECT_ROOT / "data" / "study_materials"
    }

    if folder_key in folder_map:
        return folder_map[folder_key]

    # Check for direct subfolder in user directory
    return home / folder_name


def launch_folder(folder_name: str, custom_allowlist: List[str] = None) -> Dict[str, Any]:
    """Safely open an approved directory in Windows File Explorer."""
    folder_key = folder_name.lower().strip()

    # Allowed list
    allowed = [a.lower() for a in (settings.ALLOWED_FOLDERS if isinstance(settings.ALLOWED_FOLDERS, list) else [])]
    # Add alias names
    allowed.extend(["python project", "python folder", "projects", "study materials", "documents", "downloads"])
    if custom_allowlist:
        allowed.extend([a.lower() for a in custom_allowlist])

    # Security check: verify against allowlist
    is_allowed = any(a in folder_key or folder_key in a for a in allowed)
    if not is_allowed:
        return {
            "success": False,
            "error": f"Security restriction: Folder '{folder_name}' is not in your allowed folders list.",
            "allowed_folders": allowed
        }

    try:
        resolved_path = get_canonical_folder_path(folder_name)
        # Create directory if it's a study or project directory and doesn't exist
        resolved_path.mkdir(parents=True, exist_ok=True)

        # On Windows, os.startfile opens folder in File Explorer safely
        if os.name == "nt":
            os.startfile(str(resolved_path))
        else:
            subprocess.Popen(["xdg-open", str(resolved_path)])

        return {
            "success": True,
            "folder_name": folder_name,
            "path": str(resolved_path),
            "message": f"Successfully opened folder '{folder_name}' ({resolved_path})."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to open folder '{folder_name}': {str(e)}"
        }
