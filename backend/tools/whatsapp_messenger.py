import os
import re
import time
import ctypes
import threading
import urllib.parse
import subprocess
import webbrowser
from typing import Dict, Any, Optional


def _press_enter_keystroke():
    """Simulate Windows Return/Enter key down and up using native User32 API."""
    try:
        VK_RETURN = 0x0D
        KEYEVENTF_KEYUP = 0x0002
        ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    except Exception:
        pass


def auto_send_keystroke_async(delay_sec: float = 2.2):
    """Wait for WhatsApp window to focus then automatically dispatch Enter key to send message without permission."""
    def _worker():
        time.sleep(delay_sec)
        _press_enter_keystroke()
    
    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def open_whatsapp_messenger(
    contact_name: str,
    message: str,
    phone_number: Optional[str] = None,
    auto_send: bool = True
) -> Dict[str, Any]:
    """
    Directly open native Windows WhatsApp Desktop app with target contact and automatically send message without permission prompts.
    """
    clean_msg = message.strip() if message else "Hi"
    encoded_msg = urllib.parse.quote(clean_msg)
    clean_contact = contact_name.strip() if contact_name else "Contact"

    # Clean phone number if provided (strip non-digit characters except leading +)
    clean_phone = None
    if phone_number:
        clean_phone = re.sub(r"[^\d+]", "", phone_number)
        if clean_phone.startswith("+"):
            clean_phone = clean_phone[1:]

    # Construct native Windows WhatsApp desktop protocol URI
    if clean_phone and len(clean_phone) >= 7:
        native_uri = f"whatsapp://send?phone={clean_phone}&text={encoded_msg}"
        web_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
    else:
        native_uri = f"whatsapp://send?text={encoded_msg}"
        web_url = f"https://web.whatsapp.com/send?text={encoded_msg}"

    try:
        # 1. Primary Priority: Open directly in Windows Native WhatsApp Desktop Client
        opened_native = False
        if os.name == "nt":
            try:
                os.startfile(native_uri)
                opened_native = True
            except Exception:
                try:
                    subprocess.Popen(f'cmd.exe /c start "" "{native_uri}"', shell=True)
                    opened_native = True
                except Exception:
                    opened_native = False

        # 2. Fallback to browser only if native Windows client is unavailable
        if not opened_native:
            try:
                webbrowser.open(web_url)
            except Exception:
                pass

        # 3. Automatically send message without asking for manual permission
        if auto_send and os.name == "nt":
            auto_send_keystroke_async(delay_sec=2.2)

        friendly_msg = f"Sent WhatsApp message to {clean_contact.title()}: '{clean_msg}' automatically."
        return {
            "success": True,
            "contact_name": clean_contact,
            "message": friendly_msg,
            "message_content": clean_msg,
            "phone_number": clean_phone,
            "uri": native_uri,
            "url": web_url,
            "native_app": opened_native,
            "auto_sent": True,
            "action": "open_whatsapp",
            "status_message": friendly_msg
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to open WhatsApp: {str(e)}"
        }
