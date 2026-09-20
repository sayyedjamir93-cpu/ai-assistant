# SADIE — AI Personal Assistant

> **SADIE** (*Speech & AI Desktop Intelligent Entity*) is a voice-enabled, tool-augmented AI personal assistant engineered specifically for students, developers, and computer productivity.

---

## 🌟 Key Capabilities & Features

### 🎙️ 1. Voice Assistant Pipeline
- **Microphone Input & Speech-to-Text (STT)** powered by `SpeechRecognition`.
- **Text-to-Speech (TTS)** voice synthesis powered by `gTTS` with markdown audio sanitization.
- **End-to-End Pipeline**: `Voice Input → STT → AI Brain → Intent Classifier → Security Sandbox → Tool Execution → Result → AI Response → TTS Audio Stream`.
- **Real-Time Voice Visualizer**: Animated glowing orb with reactive frequency waveforms.

### 🧠 2. AI Brain & Intent Engine
- **15 Intent Categories**: Instant classification for general questions, application launches, folder exploration, timers, notes, tasks, reminders, coding diagnostics, and memory retention.
- **Multi-Provider Architecture**: Direct support for Google Gemini, OpenAI, local Ollama LLMs, and an offline educational knowledge engine.
- **Zero Arbitrary Shell Execution**: Strict security sandbox preventing OS command injection.

### 🛡️ 3. Sandboxed Desktop Tools & Telemetry
- **YouTube & Spotify Entertainment Media Player**: On-demand song, music, and video playback (*"Play Bohemian Rhapsody on Spotify"*, *"Play Python tutorial on YouTube"*).
- **Allowlisted Application Launcher**: Safely launches approved apps (`calc.exe`, `notepad.exe`, `code`, `chrome`, `spotify`, `youtube`).
- **Allowlisted Folder Explorer**: Navigates authorized directories (`Documents`, `Projects`, `Study Materials`, `Python project`).
- **WhatsApp Messenger & Contacts**: Pre-fills and opens WhatsApp messages (*"Sadie send hii to sakshi"*).
- **Live Web Search**: Queries DuckDuckGo and Wikipedia APIs returning structured summaries and sources.
- **Hardware Telemetry**: Real-time CPU, RAM, and Disk storage monitoring.
- **User Permission Controls**: Granular per-tool permission toggles in Settings.

### 🎓 4. Dedicated Study Mode
- **Pomodoro Focus Timer**: 25m, 45m, and 60m focus blocks with circular visual countdown.
- **Break Interval Enforcement**: 5-minute short breaks and 15-minute long breaks.
- **Study Task Checklist & Analytics**: Real-time completion progress, focus time logs, and confetti celebrations.

### 💻 5. Coding Assistant & Diagnostics
- **Exception Diagnostics**: Analyzes error tracebacks (IndexError, TypeError, KeyError, RecursionError) providing meaning, causes, step-by-step fix, and defensively corrected code.
- **Concept Explainer**: In-depth breakdowns of recursion, pointers, data structures, algorithms, and OOP.
- **Code Review Sandbox**: Syntax and logic reviews for Python, C, C++, JavaScript, and HTML/CSS.

### 📋 6. Productivity Suite & Controlled Memory
- **Tasks & Reminders**: Board with completion filtering and scheduled timestamp alerts.
- **Notes with Voice Dictation**: Live keyword search and direct microphone voice-to-note capture.
- **Controlled Personal Memory**: Explicit, privacy-first fact retention with full user inspection and clear-all capability.

---

## 👥 5-Member Team Architecture & Work Allocation

| Member | Engineering Domain | Primary Modules Owned |
|---|---|---|
| **Member 1** | Frontend & UI/UX | `frontend/src/index.css`, `frontend/src/components/*`, `frontend/src/pages/*` |
| **Member 2** | Voice & Audio Systems | `backend/voice/speech_to_text.py`, `backend/voice/text_to_speech.py`, `backend/api/voice.py` |
| **Member 3** | AI Brain, NLP & Coding Assistant | `backend/ai/brain.py`, `backend/ai/intent.py`, `backend/ai/prompts.py`, `backend/api/coding.py` |
| **Member 4** | Computer Automation & Sandboxed Tools | `backend/tools/*`, `backend/ai/tool_router.py`, `backend/api/tools_api.py` |
| **Member 5** | Backend Core, Database, Auth & QA | `backend/database/*`, `backend/api/auth.py`, `backend/api/tasks.py`, `backend/tests/*` |

---

## 🚀 Quickstart & One-Click Launch (Windows)

### Option A: One-Click Launcher (Recommended)
Simply double-click:
```powershell
.\run_sadie.bat
```
*(Or run `.\run_sadie.ps1` in PowerShell)*

This starts both the FastAPI backend (`http://127.0.0.1:8000`) and the Vite React frontend (`http://localhost:5173`) in parallel.

---

### Option B: Manual Launch

#### 1. Setup Backend
```powershell
# In project root
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

#### 2. Setup Frontend
```powershell
# In a second terminal (frontend directory)
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Verification

Run the full automated test suite (54 unit, integration, and security tests):
```powershell
.\venv\Scripts\Activate.ps1
pytest backend/tests -v
```

**Test Coverage Summary:**
- `test_health.py` — Server health & database verification (2 tests)
- `test_auth.py` — Password hashing, JWT token lifecycle, and session security (6 tests)
- `test_ai_brain.py` — Intent classifier, parameter extraction, and offline fallback (12 tests)
- `test_tools.py` — Application launcher, folder explorer, web search, timers, and permissions (11 tests)
- `test_voice.py` — Speech-to-text, text-to-speech, and audio streaming pipeline (6 tests)
- `test_productivity.py` — Tasks CRUD, notes search, reminders, and memory (4 tests)
- `test_study.py` — Pomodoro timers, break manager, and analytics (2 tests)
- `test_coding.py` — Concept explainer, error diagnostics, and code reviewer (5 tests)
- `test_integration.py` — Full 8-step PBL demonstration scenario (1 test)
- `test_security_edge_cases.py` — Command injection rejection, path traversal prevention, data isolation (5 tests)

---

## 📚 Academic PBL Deliverables

- **[Full PBL Academic Project Report](file:///c:/Desktop/AI%20assistent/docs/PROJECT_REPORT_PBL.md)**: Abstract, problem statement, SRS, objectives, scope, module allocations, QA results.
- **[System Architecture & UML Diagrams](file:///c:/Desktop/AI%20assistent/docs/SYSTEM_DIAGRAMS.md)**: System architecture, DFD Level 1, end-to-end voice flowchart, and ER diagrams in Mermaid format.
- **[Presentation Slide Deck](file:///c:/Desktop/AI%20assistent/docs/PRESENTATION_SLIDES.md)**: 10-slide presentation deck with talking points for viva/evaluation.
