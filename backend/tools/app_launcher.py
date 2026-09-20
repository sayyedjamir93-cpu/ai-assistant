import os
import shutil
import subprocess
from typing import Dict, Any, List
from backend.config import settings

import webbrowser

# Canonical mapping of friendly app names to executables/commands on Windows
DEFAULT_APP_MAP: Dict[str, str] = {
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "calc.exe": "calc.exe",
    "notepad": "notepad.exe",
    "notepad.exe": "notepad.exe",
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "msedge": "msedge",
    "terminal": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "spotify": "spotify",
    "spotify.exe": "spotify.exe",
    "youtube": "youtube",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "mspaint.exe": "mspaint.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "taskmgr.exe": "taskmgr.exe",
    "settings": "ms-settings:",
    "windows settings": "ms-settings:",
    "ms-settings:": "ms-settings:",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "files": "explorer.exe",
    "explorer.exe": "explorer.exe",
    "vlc": "vlc.exe",
    "vlc.exe": "vlc.exe",
    "control panel": "control.exe",
    "control.exe": "control.exe",
    "chatgpt": "chatgpt",
    "google": "google",
    "gmail": "gmail",
    "mail": "mail",
    "email": "mail",
    "word": "winword.exe",
    "winword": "winword.exe",
    "winword.exe": "winword.exe",
    "excel": "excel.exe",
    "excel.exe": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "powerpnt": "powerpnt.exe",
    "powerpnt.exe": "powerpnt.exe",
    "snipping tool": "snippingtool.exe",
    "snippingtool": "snippingtool.exe",
    "screenshot": "snippingtool.exe",
    "camera": "microsoft.windows.camera:",
    "clock": "ms-clock:",
    "alarm": "ms-clock:",
    "whatsapp": "whatsapp",
    "whatsapp desktop": "whatsapp",
    "lock": "lock",
    "lock screen": "lock",
    "lock pc": "lock"
}


def open_target_url(url: str) -> bool:
    """Open URL or protocol URI reliably on Windows using native ShellExecute with browser fallbacks."""
    if not url:
        return False
    if os.name == "nt":
        try:
            os.startfile(url)
            return True
        except Exception:
            pass
    try:
        webbrowser.open(url)
        return True
    except Exception:
        pass
    if os.name == "nt":
        try:
            subprocess.Popen(f'cmd.exe /c start "" "{url}"', shell=True)
            return True
        except Exception:
            pass
    return False


def launch_application(app_name: str, custom_allowlist: List[str] = None, query: str = None) -> Dict[str, Any]:
    """Safely launch an approved native desktop application or web portal from the allowlist."""
    app_key = app_name.lower().strip()
    executable = DEFAULT_APP_MAP.get(app_key, app_key)

    # 1. Special handling for ChatGPT
    if app_key in ["chatgpt", "openai"]:
        import urllib.parse
        target_url = f"https://chatgpt.com/?q={urllib.parse.quote(query)}" if query else "https://chatgpt.com"
        open_target_url(target_url)
        return {
            "success": True,
            "app_name": "ChatGPT",
            "executable": target_url,
            "message": f"Successfully opened ChatGPT{f' for query: {query}' if query else ''} on Windows."
        }

    # 2. Special handling for Google Search / Google
    if app_key == "google":
        import urllib.parse
        target_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}" if query else "https://www.google.com"
        open_target_url(target_url)
        return {
            "success": True,
            "app_name": "Google",
            "executable": target_url,
            "message": f"Successfully opened Google{f' for query: {query}' if query else ''} on Windows."
        }

    # 2.5 Special handling for Chrome Browser
    if app_key in ["chrome", "google chrome", "browser", "google-chrome"]:
        chrome_candidates = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe")
        ]
        chrome_exe = next((p for p in chrome_candidates if os.path.exists(p)), None)
        if chrome_exe:
            subprocess.Popen([chrome_exe], shell=False)
            return {
                "success": True,
                "app_name": "Google Chrome",
                "executable": chrome_exe,
                "message": "Successfully opened Google Chrome on Windows."
            }
        else:
            try:
                subprocess.Popen(["cmd.exe", "/c", "start", "chrome"], shell=False)
                return {
                    "success": True,
                    "app_name": "Google Chrome",
                    "executable": "chrome",
                    "message": "Successfully opened Google Chrome."
                }
            except Exception:
                open_target_url("https://www.google.com")
                return {
                    "success": True,
                    "app_name": "Browser",
                    "executable": "https://www.google.com",
                    "message": "Opened web browser."
                }

    # 3. Special handling for Gmail / Mail / Inbox
    if app_key in ["gmail", "mail", "email", "mails", "emails", "inbox"]:
        open_target_url("https://mail.google.com")
        display = "Gmail" if "gmail" in app_key else "Mail"
        return {
            "success": True,
            "app_name": display,
            "executable": "https://mail.google.com",
            "message": f"Successfully opened {display} and your Inbox."
        }

    # 3.5 Special handling for WhatsApp native desktop app
    if app_key in ["whatsapp", "whatsapp desktop"]:
        opened = False
        if os.name == "nt":
            try:
                os.startfile("whatsapp:")
                opened = True
            except Exception:
                try:
                    subprocess.Popen('cmd.exe /c start "" "whatsapp:"', shell=True)
                    opened = True
                except Exception:
                    opened = False
        if not opened:
            open_target_url("https://web.whatsapp.com")
        return {
            "success": True,
            "app_name": "WhatsApp",
            "executable": "whatsapp:",
            "message": "Successfully opened WhatsApp on Windows."
        }

    # 4. Special handling for Lock Screen
    if app_key in ["lock", "lock screen", "lock pc", "lock laptop"]:
        try:
            if os.name == "nt":
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=False)
                return {
                    "success": True,
                    "app_name": "Windows Lock",
                    "executable": "LockWorkStation",
                    "message": "Locked Windows laptop workstation."
                }
        except Exception as e:
            return {"success": False, "error": f"Failed to lock workstation: {str(e)}"}

    # 5. Special handling for Windows URI protocols (Camera, Clock, Settings)
    if executable.startswith("ms-") or executable.startswith("microsoft."):
        try:
            if os.name == "nt":
                os.startfile(executable)
                return {
                    "success": True,
                    "app_name": app_name.title(),
                    "executable": executable,
                    "message": f"Successfully launched {app_name.title()} on Windows."
                }
        except Exception as e:
            return {"success": False, "error": f"Failed to launch {app_name}: {str(e)}"}

    # 6. Special handling for YouTube
    if app_key == "youtube":
        webbrowser.open("https://www.youtube.com")
        return {
            "success": True,
            "app_name": "YouTube",
            "executable": "https://www.youtube.com",
            "message": "Successfully opened YouTube."
        }

    # 7. Special handling for native Spotify desktop client on Windows
    if app_key in ["spotify", "spotify.exe"]:
        try:
            if os.name == "nt":
                subprocess.Popen(["cmd.exe", "/c", "start", "", "spotify:"], shell=False)
                return {
                    "success": True,
                    "app_name": "Spotify",
                    "executable": "spotify:",
                    "message": "Successfully opened Spotify Desktop on Windows."
                }
        except Exception:
            pass
        return {
            "success": True,
            "app_name": "Spotify",
            "executable": "spotify:",
            "message": "Opened Spotify Desktop."
        }

    # Get allowed applications from settings and canonical map
    allowed = set(settings.ALLOWED_APPS if isinstance(settings.ALLOWED_APPS, list) else [])
    for k, v in DEFAULT_APP_MAP.items():
        allowed.add(k.lower())
        allowed.add(v.lower())

    if custom_allowlist:
        allowed.update([a.lower() for a in custom_allowlist])

    # Security check: verify against allowlist
    if app_key not in allowed and executable not in allowed:
        return {
            "success": False,
            "error": f"Security restriction: Application '{app_name}' is not in your allowed applications list.",
            "allowed_apps": list(allowed)
        }

    try:
        # Launch native Windows application using Windows App Paths & Shell
        if os.name == "nt":
            subprocess.Popen(["cmd.exe", "/c", "start", "", executable], shell=False)
            return {
                "success": True,
                "app_name": app_name,
                "executable": executable,
                "message": f"Successfully opened {app_name.title()} on Windows."
            }
        elif shutil.which(executable) or os.path.exists(executable):
            subprocess.Popen([executable], shell=False)
            return {
                "success": True,
                "app_name": app_name,
                "executable": executable,
                "message": f"Successfully opened {app_name.title()}."
            }
        else:
            return {
                "success": False,
                "error": f"Application '{app_name}' ({executable}) was not found in system PATH."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to launch application '{app_name}': {str(e)}"
        }
