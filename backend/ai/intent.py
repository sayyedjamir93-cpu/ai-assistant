import re
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    OPEN_APPLICATION = "OPEN_APPLICATION"
    OPEN_FOLDER = "OPEN_FOLDER"
    WEB_SEARCH = "WEB_SEARCH"
    START_TIMER = "START_TIMER"
    CREATE_NOTE = "CREATE_NOTE"
    VIEW_NOTES = "VIEW_NOTES"
    CREATE_TASK = "CREATE_TASK"
    VIEW_TASKS = "VIEW_TASKS"
    GET_SYSTEM_INFO = "GET_SYSTEM_INFO"
    GET_DATETIME = "GET_DATETIME"
    START_STUDY_MODE = "START_STUDY_MODE"
    CODING_ASSISTANT = "CODING_ASSISTANT"
    REMEMBER_INFO = "REMEMBER_INFO"
    VIEW_MEMORY = "VIEW_MEMORY"
    SEND_MESSAGE = "SEND_MESSAGE"
    READ_MESSAGES = "READ_MESSAGES"
    PLAY_MEDIA = "PLAY_MEDIA"
    CONTROL_MEDIA = "CONTROL_MEDIA"
    CREATE_PROGRAM = "CREATE_PROGRAM"
    UNKNOWN = "UNKNOWN"



class IntentResult(BaseModel):
    intent: IntentType
    confidence: float = 1.0
    tool_required: bool = False
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    suggested_response: Optional[str] = None


class IntentClassifier:
    """Classifies user natural language input into structured intents and tool parameters."""

    def __init__(self):
        # Pre-compile common regex patterns for fast deterministic matching
        self._patterns = [
            # Study Mode
            (r"(?:start|begin|activate|open|enter)\s+(?:study\s+mode|study\s+session)", IntentType.START_STUDY_MODE, "study_mode", {}),
            
            # Coding Mode / Programming Help
            (r"(?:explain|debug|fix|write|help\s+with)\s+(?:python|javascript|c\+\+|html|css|recursion|algorithm|function|code|error|bug)", IntentType.CODING_ASSISTANT, "coding_assistant", {}),

            # Open Application (Native Windows desktop apps and Web Services)
            (r"(?:open|launch|start|run|go\s+to)\s+(?:the\s+)?(calculator|calc|notepad|paint|mspaint|task\s*manager|taskmgr|settings|windows\s*settings|explorer|file\s*explorer|files|vlc|vs\s*code|vscode|code|chrome|browser|browser\s+window|terminal|cmd|powershell|chatgpt|openai|google|gmail|mail|email|word|excel|powerpoint|camera|clock|alarm|snipping\s*tool|screenshot|lock\s*screen|lock\s*laptop|lock\s*pc|lock|control\s*panel)", IntentType.OPEN_APPLICATION, "open_app", {}),

            # Special Desktop Laptop Operations
            (r"(?:lock\s+(?:my\s+)?(?:laptop|pc|screen|workstation))", IntentType.OPEN_APPLICATION, "open_app", {"app_name": "lock"}),
            (r"(?:take\s+a\s+)?(?:screenshot|screen\s+snip|open\s+snipping\s+tool)", IntentType.OPEN_APPLICATION, "open_app", {"app_name": "snippingtool"}),

            # Open Folder
            (r"(?:open|show|explore)\s+(?:my\s+)?(documents|downloads|projects|study\s+materials|desktop|music|videos|folder|directory|python\s+project|files|workspace)", IntentType.OPEN_FOLDER, "open_folder", {}),

            # Timer
            (r"(?:start|set|create)\s+(?:a\s+)?(?:timer\s+(?:for\s+)?)?(\d+)\s*(?:min|minute|minutes|sec|second|seconds|hour|hours)(?:\s+timer)?", IntentType.START_TIMER, "timer", {}),

            # Note Creation
            (r"(?:create|add|make|take|save)\s+(?:a\s+)?note(?:\s*[:\-]\s*|\s+(?:that|about)\s+)(.+)", IntentType.CREATE_NOTE, "create_note", {}),
            (r"(?:view|show|list|get)\s+(?:my\s+)?notes", IntentType.VIEW_NOTES, "view_notes", {}),

            # Task & Reminder
            (r"(?:remind\s+me\s+to|add\s+task|create\s+task)(?:\s*[:\-]\s*|\s+)(.+)", IntentType.CREATE_TASK, "create_task", {}),
            (r"(?:view|show|list|get)\s+(?:my\s+)?(?:tasks|to-do|todos)", IntentType.VIEW_TASKS, "view_tasks", {}),

            # System Information
            (r"(?:show|check|get|display)\s+(?:my\s+)?(?:system|sys)\s*(?:info|information|specs|status)", IntentType.GET_SYSTEM_INFO, "system_info", {}),

            # Date / Time
            (r"(?:what\s+(?:is\s+the\s+)?time|what\s+time\s+is\s+it|current\s+time|what\s+is\s+today'?s?\s+date|current\s+date)", IntentType.GET_DATETIME, "datetime", {}),

            # Web Search
            (r"(?:search\s+(?:the\s+web\s+for|google\s+for|for)|web\s+search|look\s+up)\s+(.+)", IntentType.WEB_SEARCH, "web_search", {}),

            # Memory
            (r"(?:remember\s+(?:that\s+)?|store\s+(?:that\s+)?)(.+)", IntentType.REMEMBER_INFO, "remember_info", {}),
            (r"(?:what\s+do\s+you\s+remember|show\s+memories|view\s+memory)", IntentType.VIEW_MEMORY, "view_memory", {})
        ]

    def classify_rule_based(self, text: str) -> IntentResult:
        """Rule-based pattern matching for rapid, offline-capable intent detection."""
        clean_text = text.strip()
        lower_text = clean_text.lower()

        # -2. Create Program / Code Project in VS Code (e.g. "create sum program on python language", "write a calculator in javascript", "create python program to calculate sum")
        SUPPORTED_LANGS = [
            "python", "py", "javascript", "js", "typescript", "ts",
            "cpp", "c++", "c", "java", "html", "css", "rust", "go",
            "golang", "c#", "csharp", "php", "ruby", "kotlin", "sql", "bash"
        ]

        # Pattern A: 'create [lang] program to/for [task]' (e.g. 'create python program to calculate sum')
        m_prog_p1 = re.search(r"(?:sadie\s+)?(?:open\s+vs\s*code\s+(?:and\s+)?)?(?:create|write|make|build|code|generate)\s+(?:a\s+)?([a-zA-Z\+\#]+)\s+(?:program|script|app|code|project|file)?\s*(?:to|for|about|that\s+does)\s+(.+)", lower_text)
        
        # Pattern B: 'create [task] program in/on [lang] language' (e.g. 'create sum program on python language')
        m_prog_p2 = re.search(r"(?:sadie\s+)?(?:open\s+vs\s*code\s+(?:and\s+)?)?(?:create|write|make|build|code|generate)\s+(?:a\s+)?(.+?)\s*(?:program|script|app|code|project|file)?\s*(?:in|on|with|using)\s+([a-zA-Z\+\#]+)(?:\s+(?:language|lang))?(?:\s+(?:to|for|about)\s+(.+))?", lower_text)

        if m_prog_p1 and m_prog_p1.group(1).lower() in SUPPORTED_LANGS:
            lang_match = m_prog_p1.group(1).lower()
            task_match = m_prog_p1.group(2).strip()
            norm_lang = "cpp" if lang_match == "c++" else ("csharp" if lang_match == "c#" else lang_match)
            return IntentResult(
                intent=IntentType.CREATE_PROGRAM,
                confidence=0.99,
                tool_required=True,
                tool_name="create_code_file",
                parameters={"language": norm_lang, "task_description": task_match, "open_editor": True},
                suggested_response=f"I've created your {norm_lang.upper()} program for '{task_match}' and opened it in VS Code on Windows."
            )

        if m_prog_p2 and m_prog_p2.group(2).lower() in SUPPORTED_LANGS:
            lang_match = m_prog_p2.group(2).lower()
            task_base = re.sub(r"^(?:a\s+)?", "", m_prog_p2.group(1) or "").strip()
            task_base = re.sub(r"\s*(?:program|script|app|code|file)$", "", task_base).strip()
            extra = (m_prog_p2.group(3) or "").strip()
            full_task = f"{task_base} {extra}".strip() if extra else (task_base or "program")
            norm_lang = "cpp" if lang_match == "c++" else ("csharp" if lang_match == "c#" else lang_match)
            return IntentResult(
                intent=IntentType.CREATE_PROGRAM,
                confidence=0.99,
                tool_required=True,
                tool_name="create_code_file",
                parameters={"language": norm_lang, "task_description": full_task, "open_editor": True},
                suggested_response=f"I've created your {norm_lang.upper()} program for '{full_task}' and opened it in VS Code on Windows."
            )

        # -1.5. ChatGPT Direct Assistant Invocation (e.g. "ask chatgpt how to make a game", "open chatgpt", "search chatgpt for python")
        m_chatgpt = re.search(r"(?:sadie\s+)?(?:(?:ask|search)\s+chatgpt\s+(?:for|about|to)?\s*(.+)|(?:open|launch|go\s+to)\s+chatgpt(?:\s+(?:and\s+)?(?:ask|search\s+for)?\s*(.*))?)", lower_text)
        if m_chatgpt:
            gpt_q = (m_chatgpt.group(1) or m_chatgpt.group(2) or "").strip()
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "chatgpt", "query": gpt_q if gpt_q else None},
                suggested_response=f"Opening ChatGPT on Windows{f' with query: {gpt_q}' if gpt_q else '.'}"
            )

        # -1.4. Chrome / Browser Quick Open (e.g. "open chrome", "sadie open chrome", "open google chrome", "open browser")
        m_chrome = re.search(r"(?:sadie\s+)?(?:open|launch|start|run)\s+(?:the\s+)?(chrome|google\s+chrome|browser|browser\s+window)", lower_text)
        if m_chrome:
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "chrome"},
                suggested_response="Opening Google Chrome on Windows."
            )

        # -1.35. Google Direct Search & Open (e.g. "search google for weather", "google python tutorials", "open google")
        m_google = re.search(r"(?:sadie\s+)?(?:search\s+google\s+(?:for\s+)?(.+)|google\s+(.+)|(?:open|launch|go\s+to)\s+google(?:\s+(?:and\s+)?(?:search\s+for)?\s*(.*))?)", lower_text)
        if m_google:
            g_query = (m_google.group(1) or m_google.group(2) or m_google.group(3) or "").strip()
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "google", "query": g_query if g_query else None},
                suggested_response=f"Opening Google on Windows{f' for {g_query}' if g_query else '.'}"
            )

        # -1.3. Mail & Gmail Quick Check / Open (e.g. "check my mails", "check my mail", "check emails", "check inbox", "open mail", "open gmail")
        m_mail = re.search(r"(?:sadie\s+)?(?:open|launch|go\s+to|compose|check|read|view|show|see|look\s+at)\s+(?:my\s+)?(gmail|mails?|emails?|inbox)", lower_text)
        if m_mail:
            target_mail = m_mail.group(1).lower()
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "gmail" if "gmail" in target_mail else "mail"},
                suggested_response="Opening your Mail and Inbox on Windows."
            )

        # -1.2. File Explorer & Files Quick Open (e.g. "open files", "open file explorer", "open explorer")
        m_files = re.search(r"(?:sadie\s+)?(?:open|show|explore|launch)\s+(?:my\s+)?(files|file\s+explorer|explorer)", lower_text)
        if m_files:
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "explorer.exe"},
                suggested_response="Opening Windows File Explorer."
            )

        # -1.1. Lock Laptop / Workstation
        m_lock = re.search(r"(?:sadie\s+)?lock\s+(?:my\s+)?(?:laptop|pc|computer|screen|workstation)", lower_text)
        if m_lock:
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.99,
                tool_required=True,
                tool_name="open_app",
                parameters={"app_name": "lock"},
                suggested_response="Locking your Windows laptop workstation."
            )

        # -1. Windows Native Media Playback & Volume Control
        m_media_ctrl = re.search(r"(?:sadie\s+)?(?:(pause|stop|resume|unpause)\s+(?:the\s+)?(?:music|song|video|media|track|playback|spotify)|(next|skip)\s+(?:song|this|track)|(previous|prev)\s+(?:song|track)|(?:increase\s+volume|volume\s+up|louder|make\s+it\s+louder)|(?:decrease\s+volume|volume\s+down|lower\s+volume|quieter|make\s+it\s+quieter)|(?:mute\s+volume|mute\s+audio|mute\s+sound|unmute\s+volume|unmute\s+audio))", lower_text)
        if m_media_ctrl:
            if any(w in lower_text for w in ["pause", "stop"]):
                act = "play_pause"
                resp = "Paused playback on Windows."
            elif any(w in lower_text for w in ["resume", "unpause"]):
                act = "play_pause"
                resp = "Resumed playback on Windows."
            elif any(w in lower_text for w in ["next", "skip"]):
                act = "next"
                resp = "Skipping to next track on Windows."
            elif any(w in lower_text for w in ["previous", "prev", "back"]):
                act = "previous"
                resp = "Skipping to previous track on Windows."
            elif any(w in lower_text for w in ["volume up", "increase volume", "louder"]):
                act = "volume_up"
                resp = "Increased Windows volume."
            elif any(w in lower_text for w in ["volume down", "decrease volume", "lower volume", "quieter"]):
                act = "volume_down"
                resp = "Decreased Windows volume."
            elif any(w in lower_text for w in ["mute", "unmute", "silence"]):
                act = "mute"
                resp = "Toggled Windows volume mute."
            else:
                act = "play_pause"
                resp = "Toggled Windows media playback."

            return IntentResult(
                intent=IntentType.CONTROL_MEDIA,
                confidence=0.98,
                tool_required=True,
                tool_name="control_media",
                parameters={"action": act},
                suggested_response=resp
            )

        # 0. Media Player: YouTube & Spotify Playback & Opening (e.g. "play bohemian rhapsody on youtube", "play starboy on spotify", "open youtube", "open spotify")
        # Pattern A: "open youtube/spotify and play/search [query]"
        m_open_play = re.search(r"(?:sadie\s+)?(?:open|launch|start)\s+(youtube|spotify)\s+(?:and\s+)?(?:play|search(?:\s+for)?|listen\s+to|watch)\s+(.+)", lower_text)
        if m_open_play:
            platform = m_open_play.group(1).lower()
            query_raw = clean_text[m_open_play.start(2):m_open_play.end(2)].strip()
            clean_query = re.sub(r"^(?:the\s+)?(?:song|track|video|music|clip)\s+", "", query_raw, flags=re.IGNORECASE).strip()
            return IntentResult(
                intent=IntentType.PLAY_MEDIA,
                confidence=0.98,
                tool_required=True,
                tool_name="play_media",
                parameters={"platform": platform, "query": clean_query},
                suggested_response=f"Playing '{clean_query}' on {platform.title()}."
            )

        # Pattern B: "play [query] on/in [youtube/spotify]"
        m_play_on = re.search(r"(?:sadie\s+)?(?:play|stream|listen\s+to|watch)\s+(.+?)\s+(?:on|in|from|via)\s+(youtube|spotify)", lower_text)
        if m_play_on:
            platform = m_play_on.group(2).lower()
            query_raw = clean_text[m_play_on.start(1):m_play_on.end(1)].strip()
            clean_query = re.sub(r"^(?:the\s+)?(?:song|track|video|music|clip)\s+", "", query_raw, flags=re.IGNORECASE).strip()
            return IntentResult(
                intent=IntentType.PLAY_MEDIA,
                confidence=0.98,
                tool_required=True,
                tool_name="play_media",
                parameters={"platform": platform, "query": clean_query},
                suggested_response=f"Playing '{clean_query}' on {platform.title()}."
            )

        # Pattern C: "search youtube/spotify for [query]"
        m_search_plat = re.search(r"(?:sadie\s+)?(?:search\s+(?:on\s+)?(youtube|spotify)\s+for|(youtube|spotify)\s+search\s+for)\s+(.+)", lower_text)
        if m_search_plat:
            platform = (m_search_plat.group(1) or m_search_plat.group(2)).lower()
            query_raw = clean_text[m_search_plat.start(3):m_search_plat.end(3)].strip()
            return IntentResult(
                intent=IntentType.PLAY_MEDIA,
                confidence=0.97,
                tool_required=True,
                tool_name="play_media",
                parameters={"platform": platform, "query": query_raw},
                suggested_response=f"Searching for '{query_raw}' on {platform.title()}."
            )

        # Pattern D: Direct "open youtube" / "open spotify"
        m_open_plat = re.search(r"^(?:sadie\s+)?(?:open|launch|start)\s+(youtube|spotify)(?:\s+(?:app|website|music|web))?$", lower_text)
        if m_open_plat:
            platform = m_open_plat.group(1).lower()
            return IntentResult(
                intent=IntentType.PLAY_MEDIA,
                confidence=0.96,
                tool_required=True,
                tool_name="play_media",
                parameters={"platform": platform, "query": ""},
                suggested_response=f"Opening {platform.title()}."
            )

        # Pattern E: Song / Music Recommendation with automatic playback
        # e.g., "suggest me a song", "suggest a song and play it", "recommend a song", "suggest music", "what song should I listen to"
        m_suggest_song = re.search(
            r"(?:sadie\s+)?(?:suggest|recommend|give\s+me)\s+(?:me\s+)?(?:a\s+|some\s+)?(?:good\s+|nice\s+|relaxing\s+|chill\s+|cool\s+|popular\s+)?(?:song|music|track|tune|video|album)(?:\s+(?:and|to)\s+(?:play|listen|watch)(?:\s+it)?)?",
            lower_text
        )
        m_play_generic_song = re.search(
            r"^(?:sadie\s+)?(?:play|stream|listen\s+to)\s+(?:a\s+|some\s+)?(?:random\s+|good\s+|any\s+|nice\s+)?(?:song|music|track|tune|something)(?:\s+for\s+me|\s+please)?$",
            lower_text
        )
        if m_suggest_song or m_play_generic_song:
            platform = "spotify" if "spotify" in lower_text else "youtube"
            if any(w in lower_text for w in ["chill", "relax", "study", "peaceful", "calm"]):
                recommended_song = "Lofi Hip Hop Radio - Beats to Relax/Study to"
            elif any(w in lower_text for w in ["energy", "workout", "rock", "hype", "pump"]):
                recommended_song = "Believer - Imagine Dragons"
            elif any(w in lower_text for w in ["pop", "dance", "synth", "party"]):
                recommended_song = "Starboy - The Weeknd"
            elif any(w in lower_text for w in ["classic", "legend", "anthem"]):
                recommended_song = "Bohemian Rhapsody - Queen"
            else:
                recommended_song = "Bohemian Rhapsody - Queen"

            return IntentResult(
                intent=IntentType.PLAY_MEDIA,
                confidence=0.97,
                tool_required=True,
                tool_name="play_media",
                parameters={"platform": platform, "query": recommended_song},
                suggested_response=f"I recommend '{recommended_song}'! Playing it for you now on {platform.title()}."
            )

        # Pattern F: Generic "play [song/music/video]" without specifying platform (default to youtube / spotify if mentioned)
        m_gen_play = re.search(r"^(?:sadie\s+)?(?:play|stream|listen\s+to)\s+(.+)$", lower_text)
        if m_gen_play:
            query_raw = clean_text[m_gen_play.start(1):m_gen_play.end(1)].strip()
            # Guard against commands like "play game" or non-music phrases
            if query_raw and not any(query_raw.lower().startswith(x) for x in ["timer", "game", "study", "role"]):
                clean_query = re.sub(r"^(?:the\s+)?(?:song|track|video|music|clip)\s+", "", query_raw, flags=re.IGNORECASE).strip()
                clean_query = re.sub(r"\s+(?:for\s+me|please)$", "", clean_query, flags=re.IGNORECASE).strip()
                
                # If query is generic like "a song" or "something", recommend top track
                if clean_query.lower() in ["a song", "song", "some song", "music", "some music", "a video", "video", "something", "anything", ""]:
                    clean_query = "Bohemian Rhapsody - Queen"

                platform = "spotify" if "spotify" in lower_text else "youtube"
                return IntentResult(
                    intent=IntentType.PLAY_MEDIA,
                    confidence=0.94,
                    tool_required=True,
                    tool_name="play_media",
                    parameters={"platform": platform, "query": clean_query},
                    suggested_response=f"Playing '{clean_query}' on {platform.title()}."
                )

        # 0.4. Read / Check WhatsApp Messages & Incoming Notifications
        if re.search(r"\b(?:read|check|show|tell me|view|listen to|any)\s+(?:my\s+)?(?:new\s+)?(?:whatsapp\s+messages?|messages?|incoming\s+messages?|notifications?|texts?)\b|\b(?:who\s+(?:sent\s+me\s+a\s+message|messaged\s+me|texted\s+me)|do\s+i\s+have\s+any\s+(?:new\s+)?(?:whatsapp\s+)?messages?|read\s+latest\s+message)\b", lower_text):
            return IntentResult(
                intent=IntentType.READ_MESSAGES,
                confidence=0.98,
                tool_required=True,
                tool_name="read_messages",
                parameters={},
                suggested_response="Checking your WhatsApp and incoming messages."
            )

        # 0.5. WhatsApp / Contact Messaging (e.g. "open whatsapp and say hi to sakshi", "send hii to sakshi")
        # Variation 1: "open whatsapp and (say/send/text/message) [msg] to [contact]"
        v1 = re.search(r"(?:sadie\s+)?(?:open\s+whatsapp\s+(?:and\s+)?)(?:say|send|text|message)\s+(.+?)\s+to\s+([a-zA-Z0-9_\s]+)", lower_text)
        # Variation 2: "(send/say/text/message/tell) [msg] to [contact]"
        v2 = re.search(r"(?:sadie\s+)?(?:send|text|message|say|tell)\s+(?:a\s+)?(?:whatsapp\s+)?(?:message\s+)?(.+?)\s+to\s+([a-zA-Z0-9_\s]+)", lower_text)
        # Variation 3: "open whatsapp (and) (message/text/send to) [contact] (saying/that/:) [msg]"
        v3 = re.search(r"(?:sadie\s+)?(?:open\s+whatsapp\s+(?:and\s+)?)?(?:send\s+(?:message\s+)?to|message|whatsapp|text|tell)\s+([a-zA-Z0-9_]+)\s*(?:[:\-]\s*|\s+(?:saying|that)\s+|\s+)(.+)", lower_text)
        
        match_result = None
        if v1:
            match_result = (clean_text[v1.start(2):v1.end(2)].strip(), clean_text[v1.start(1):v1.end(1)].strip())
        elif v2:
            match_result = (clean_text[v2.start(2):v2.end(2)].strip(), clean_text[v2.start(1):v2.end(1)].strip())
        elif v3:
            match_result = (clean_text[v3.start(1):v3.end(1)].strip(), clean_text[v3.start(2):v3.end(2)].strip())

        if match_result:
            contact_target, msg_content = match_result
            # Clean punctuation from end of contact name if any
            contact_target = re.sub(r"[^\w\s]", "", contact_target).strip()
            msg_content = msg_content.strip()
            return IntentResult(
                intent=IntentType.SEND_MESSAGE,
                confidence=0.96,
                tool_required=True,
                tool_name="send_whatsapp",
                parameters={"contact_name": contact_target, "message": msg_content},
                suggested_response=f"Sending WhatsApp message '{msg_content}' to {contact_target.title()} automatically."
            )


        # 1. Study Mode

        if re.search(r"\b(study mode|start study|begin study)\b", lower_text):
            subject_match = re.search(r"study\s+(?:mode\s+for\s+|session\s+for\s+)?([a-zA-Z0-9_\s]+)", lower_text)
            subject = subject_match.group(1).strip() if subject_match and "mode" not in subject_match.group(1) else "General Studies"
            return IntentResult(
                intent=IntentType.START_STUDY_MODE,
                confidence=0.98,
                tool_required=True,
                tool_name="study_mode",
                parameters={"subject": subject},
                suggested_response=f"Activating Study Mode for {subject}. Let's focus and get productive!"
            )

        # 2. Timer
        timer_match = re.search(r"(?:start|set|create)\s+(?:a\s+)?(?:(\d+)\s*(?:min|minute|minutes)|(\d+)\s*(?:sec|second|seconds)|(\d+)\s*(?:hour|hours))(?:\s+timer)?", lower_text)
        if timer_match:
            mins = int(timer_match.group(1)) if timer_match.group(1) else 0
            secs = int(timer_match.group(2)) if timer_match.group(2) else 0
            hours = int(timer_match.group(3)) if timer_match.group(3) else 0
            total_minutes = (hours * 60) + mins + (1 if (secs > 0 and mins == 0 and hours == 0) else round(secs / 60, 2))
            if total_minutes == 0:
                total_minutes = 25 # Default pomodoro
            return IntentResult(
                intent=IntentType.START_TIMER,
                confidence=0.95,
                tool_required=True,
                tool_name="start_timer",
                parameters={"duration_minutes": total_minutes, "label": f"{total_minutes} min timer"},
                suggested_response=f"Starting a {total_minutes} minute timer for you."
            )

        # 3. Open Application
        app_match = re.search(r"(?:open|launch|start|run)\s+(?:the\s+)?(calculator|calc|notepad|vs\s*code|vscode|code|chrome|browser|terminal)", lower_text)
        if app_match:
            app_raw = app_match.group(1).lower().replace(" ", "")
            app_map = {
                "calculator": "calc.exe",
                "calc": "calc.exe",
                "notepad": "notepad.exe",
                "vscode": "code",
                "code": "code",
                "chrome": "chrome",
                "browser": "chrome",
                "terminal": "cmd.exe"
            }
            app_target = app_map.get(app_raw, app_raw)
            return IntentResult(
                intent=IntentType.OPEN_APPLICATION,
                confidence=0.97,
                tool_required=True,
                tool_name="open_application",
                parameters={"app_name": app_target, "display_name": app_match.group(1).title()},
                suggested_response=f"Opening {app_match.group(1).title()}."
            )

        # 4. Open Folder
        folder_match = re.search(r"(?:open|show|explore)\s+(?:my\s+)?(documents|downloads|projects|study\s+materials|python\s+project|python\s+folder)", lower_text)
        if folder_match:
            target = folder_match.group(1).strip()
            return IntentResult(
                intent=IntentType.OPEN_FOLDER,
                confidence=0.96,
                tool_required=True,
                tool_name="open_folder",
                parameters={"folder_name": target},
                suggested_response=f"Opening your {target.title()} folder."
            )

        # 5. Note creation
        note_match = re.search(r"(?:create|add|make|take|save)\s+(?:a\s+)?note(?:\s*[:\-]\s*|\s+(?:that|about)\s+|\s+)(.+)", lower_text)
        if note_match:
            note_content = clean_text[note_match.start(1):].strip()
            title = note_content.split(".")[0][:50]
            return IntentResult(
                intent=IntentType.CREATE_NOTE,
                confidence=0.94,
                tool_required=True,
                tool_name="create_note",
                parameters={"title": title, "content": note_content},
                suggested_response=f"Note created: '{title}'"
            )

        # 6. View Notes
        if re.search(r"\b(view|show|list|get)\s+(?:my\s+)?notes\b", lower_text):
            return IntentResult(
                intent=IntentType.VIEW_NOTES,
                confidence=0.95,
                tool_required=True,
                tool_name="view_notes",
                parameters={},
                suggested_response="Here are your saved notes."
            )

        # 7. Tasks & Reminders
        task_match = re.search(r"(?:remind\s+me\s+to|add\s+task|create\s+task)(?:\s*[:\-]\s*|\s+)(.+)", lower_text)
        if task_match:
            task_desc = clean_text[task_match.start(1):].strip()
            return IntentResult(
                intent=IntentType.CREATE_TASK,
                confidence=0.93,
                tool_required=True,
                tool_name="create_task",
                parameters={"title": task_desc},
                suggested_response=f"Reminder created for: '{task_desc}'"
            )

        # 8. View Tasks
        if re.search(r"\b(view|show|list|get)\s+(?:my\s+)?(?:tasks|todos|to-do)\b", lower_text):
            return IntentResult(
                intent=IntentType.VIEW_TASKS,
                confidence=0.95,
                tool_required=True,
                tool_name="view_tasks",
                parameters={},
                suggested_response="Here are your pending tasks."
            )

        # 9. System Info
        if re.search(r"\b(system\s+info|sys\s*info|system\s+information|specs|cpu\s+usage|ram\s+usage)\b", lower_text):
            return IntentResult(
                intent=IntentType.GET_SYSTEM_INFO,
                confidence=0.98,
                tool_required=True,
                tool_name="system_info",
                parameters={},
                suggested_response="Retrieving your system specifications and resource usage."
            )

        # 10. Date / Time
        if re.search(r"\b(what\s+time|current\s+time|what\s+is\s+today'?s?\s+date|current\s+date|what\s+day\s+is\s+it)\b", lower_text):
            return IntentResult(
                intent=IntentType.GET_DATETIME,
                confidence=0.98,
                tool_required=True,
                tool_name="datetime",
                parameters={},
                suggested_response="Checking current date and time."
            )

        # 11. Memory: Remember Information
        mem_match = re.search(r"(?:remember\s+(?:that\s+)?|store\s+(?:that\s+)?)(.+)", lower_text)
        if mem_match:
            mem_val = clean_text[mem_match.start(1):].strip()
            key_candidate = mem_val.split(" is ")[0] if " is " in mem_val else mem_val[:40]
            return IntentResult(
                intent=IntentType.REMEMBER_INFO,
                confidence=0.92,
                tool_required=True,
                tool_name="remember_info",
                parameters={"key": key_candidate.strip(), "value": mem_val},
                suggested_response=f"I will remember that {mem_val}."
            )

        # 12. View Memory
        if re.search(r"\b(what\s+do\s+you\s+remember|view\s+memory|show\s+memories|my\s+memories)\b", lower_text):
            return IntentResult(
                intent=IntentType.VIEW_MEMORY,
                confidence=0.95,
                tool_required=True,
                tool_name="view_memory",
                parameters={},
                suggested_response="Here is everything stored in my memory."
            )

        # 13. Web Search
        search_match = re.search(r"(?:search\s+(?:the\s+web\s+for|google\s+for|for)|web\s+search|look\s+up)\s+(.+)", lower_text)
        if search_match:
            query = clean_text[search_match.start(1):].strip()
            return IntentResult(
                intent=IntentType.WEB_SEARCH,
                confidence=0.91,
                tool_required=True,
                tool_name="web_search",
                parameters={"query": query},
                suggested_response=f"Searching the web for '{query}'."
            )

        # 14. Coding / Programming Concept (e.g., Python recursion)
        if re.search(r"\b(recursion|python|javascript|typescript|c\+\+|java|html|css|sql|function|algorithm|class|data structure|binary search|sorting|loop|array|linked list)\b", lower_text):
            return IntentResult(
                intent=IntentType.CODING_ASSISTANT,
                confidence=0.88,
                tool_required=False,
                tool_name=None,
                parameters={"topic": clean_text},
                suggested_response=None
            )

        # Fallback to General Conversation
        return IntentResult(
            intent=IntentType.GENERAL_CONVERSATION,
            confidence=0.80,
            tool_required=False,
            tool_name=None,
            parameters={},
            suggested_response=None
        )


intent_classifier = IntentClassifier()
