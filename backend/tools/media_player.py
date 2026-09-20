import os
import re
import urllib.parse
import webbrowser
import subprocess
import httpx
import ctypes
from typing import Dict, Any, Optional

# Windows Virtual Key Codes for Media & Volume Control
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF


def press_windows_key(vk_code: int):
    """Simulate a native Windows hardware key press and release."""
    if os.name == "nt":
        try:
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
            return True
        except Exception:
            return False
    return False


def control_windows_media(action: str) -> Dict[str, Any]:
    """
    Control Windows system media playback and volume natively without browser dependency.
    
    Supported actions:
        - 'play_pause' / 'toggle': Play or pause current active music/video (Spotify, VLC, Windows Media)
        - 'next': Skip to the next track
        - 'previous' / 'prev': Go to previous track
        - 'volume_up': Increase Windows master volume
        - 'volume_down': Decrease Windows master volume
        - 'mute': Mute/unmute Windows master volume
    """
    act = (action or "").lower().strip()
    
    if act in ["play", "pause", "play_pause", "toggle", "resume"]:
        success = press_windows_key(VK_MEDIA_PLAY_PAUSE)
        msg = "Toggled playback (Play/Pause) on Windows."
    elif act in ["next", "skip", "next_track"]:
        success = press_windows_key(VK_MEDIA_NEXT_TRACK)
        msg = "Skipped to next track on Windows."
    elif act in ["prev", "previous", "previous_track", "back"]:
        success = press_windows_key(VK_MEDIA_PREV_TRACK)
        msg = "Skipped to previous track on Windows."
    elif act in ["volume_up", "vol_up", "louder", "increase_volume"]:
        # Press 3 times for a noticeable step
        for _ in range(3):
            press_windows_key(VK_VOLUME_UP)
        success = True
        msg = "Increased Windows system volume."
    elif act in ["volume_down", "vol_down", "quieter", "decrease_volume"]:
        for _ in range(3):
            press_windows_key(VK_VOLUME_DOWN)
        success = True
        msg = "Decreased Windows system volume."
    elif act in ["mute", "unmute", "silence"]:
        success = press_windows_key(VK_VOLUME_MUTE)
        msg = "Toggled Windows volume mute."
    else:
        return {
            "success": False,
            "action": act,
            "error": f"Unknown media control action '{action}'. Supported: play_pause, next, previous, volume_up, volume_down, mute."
        }

    return {
        "success": success,
        "action": act,
        "message": msg,
        "status_message": msg
    }


def resolve_youtube_direct_play(query: str) -> Dict[str, Optional[str]]:
    """
    Search YouTube and resolve the exact top video ID to enable direct instant playback.
    """
    clean_query = query.strip()
    encoded_query = urllib.parse.quote_plus(clean_query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    video_id = None
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(timeout=3.0, follow_redirects=True) as client:
            resp = client.get(search_url, headers=headers)
            if resp.status_code == 200:
                ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', resp.text)
                if not ids:
                    ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
                if ids:
                    video_id = ids[0]
    except Exception:
        video_id = None

    if video_id:
        watch_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
    else:
        watch_url = search_url
        embed_url = None

    return {
        "video_id": video_id,
        "watch_url": watch_url,
        "embed_url": embed_url,
        "search_url": search_url
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


def play_media(
    platform: str = "youtube",
    query: Optional[str] = None,
    media_type: Optional[str] = "media"
) -> Dict[str, Any]:
    """
    Directly play requested songs, music tracks, videos, and tutorials on Spotify or YouTube.
    For Spotify, opens and plays directly in the native Windows Spotify desktop client.
    """
    norm_platform = (platform or "youtube").lower().strip()
    norm_query = (query or "").strip()
    
    if norm_query:
        norm_query = norm_query.strip(".!?,")

    if "spotify" in norm_platform:
        platform_key = "spotify"
    else:
        platform_key = "youtube"

    try:
        if platform_key == "spotify":
            if norm_query:
                encoded_query = urllib.parse.quote(norm_query)
                spotify_uri = f"spotify:search:{encoded_query}"
                web_url = f"https://open.spotify.com/search/{encoded_query}"
                embed_url = f"https://open.spotify.com/embed/search/{encoded_query}"
                
                # Launch native Windows Spotify desktop application or Web Player
                launched_native = open_target_url(spotify_uri)
                if not launched_native:
                    open_target_url(web_url)

                resolved_yt = resolve_youtube_direct_play(norm_query)
                friendly_msg = f"Playing '{norm_query}' in Spotify on Windows."
                return {
                    "success": True,
                    "platform": "spotify",
                    "query": norm_query,
                    "action": "play_spotify",
                    "uri": spotify_uri,
                    "url": web_url,
                    "embed_url": embed_url,
                    "youtube_fallback_url": resolved_yt.get("watch_url"),
                    "youtube_embed_url": resolved_yt.get("embed_url"),
                    "native_app": launched_native,
                    "message": friendly_msg,
                    "status_message": friendly_msg
                }
            else:
                launched_native = open_target_url("spotify:")
                if not launched_native:
                    open_target_url("https://open.spotify.com")

                friendly_msg = "Opened Spotify on Windows."
                return {
                    "success": True,
                    "platform": "spotify",
                    "query": "",
                    "action": "open_spotify",
                    "uri": "spotify:",
                    "url": "https://open.spotify.com",
                    "embed_url": "https://open.spotify.com/embed",
                    "native_app": launched_native,
                    "message": friendly_msg,
                    "status_message": friendly_msg
                }

        else: # YouTube Direct Play
            if norm_query:
                resolved = resolve_youtube_direct_play(norm_query)
                direct_url = resolved["watch_url"]
                open_target_url(direct_url)
                
                friendly_msg = f"Playing '{norm_query}' on YouTube."
                return {
                    "success": True,
                    "platform": "youtube",
                    "query": norm_query,
                    "video_id": resolved.get("video_id"),
                    "action": "play_youtube",
                    "url": direct_url,
                    "embed_url": resolved.get("embed_url"),
                    "search_url": resolved.get("search_url"),
                    "message": friendly_msg,
                    "status_message": friendly_msg
                }
            else:
                youtube_url = "https://www.youtube.com"
                open_target_url(youtube_url)
                
                friendly_msg = "Opened YouTube."
                return {
                    "success": True,
                    "platform": "youtube",
                    "query": "",
                    "video_id": None,
                    "action": "open_youtube",
                    "url": youtube_url,
                    "embed_url": None,
                    "message": friendly_msg,
                    "status_message": friendly_msg
                }

    except Exception as e:
        return {
            "success": False,
            "platform": platform_key,
            "query": norm_query,
            "error": f"Failed to play media on {platform_key.title()}: {str(e)}"
        }
