# SADIE: College PBL Final Presentation Deck
## Slide-by-Slide Presentation Structure & Talking Points

---

### Slide 1: Title & Team
- **Title:** SADIE — Voice-Enabled AI Personal Assistant
- **Subtitle:** Bridging Natural Language, Safe Desktop Automation, and Academic Productivity
- **Team Roles:** 5-Member Engineering Team (Frontend, Voice/Audio, AI/NLP, Desktop Automation, Backend/Database)
- **Tech Stack:** FastAPI, React 18, Vite, SQLAlchemy, SQLite, SpeechRecognition, gTTS, Bcrypt

---

### Slide 2: Problem Statement & Motivation
- **Context Switching Tax:** Students switch apps over 30 times an hour between study timers, calculators, code editors, search tabs, and notes.
- **The Chatbot Limitation:** Existing LLMs are text-only conversational bots that cannot interact with the operating system safely.
- **Security Hazards:** Unrestricted terminal execution in AI assistants causes catastrophic command injection risks.

---

### Slide 3: Solution & Core Architecture
- **Voice-to-Action Pipeline:**
  $$\text{Voice Input} \rightarrow \text{STT} \rightarrow \text{AI Brain} \rightarrow \text{Intent Engine} \rightarrow \text{Security Sandbox} \rightarrow \text{Tool Execution} \rightarrow \text{Response} \rightarrow \text{TTS}$$
- **Zero Arbitrary Shell Execution:** Strict allowlists for approved apps and safe folders.
- **Modular 3-Tier Architecture:** React Glassmorphic UI $\leftrightarrow$ FastAPI REST API $\leftrightarrow$ SQLite ORM.

---

### Slide 4: AI Brain & Intent Engine
- **15 Distinct Intent Categories:** Detects everything from coding diagnostics to timers, folders, app launching, and memory facts.
- **Deterministic & Heuristic NLP:** Sub-50ms offline classification with multi-provider LLM support (Gemini, OpenAI, Ollama).
- **Context & Memory Injection:** Transparent memory facts injected into conversational context.

---

### Slide 5: Sandboxed Tool Framework & Security Gate
- **Application Launcher:** Safe process spawning without `shell=True` for allowlisted applications (`calc.exe`, `notepad.exe`, `code`, `chrome`).
- **Folder Explorer:** Direct Windows Explorer navigation to authorized project and study directories.
- **Web Search Tool:** Real-time retrieval via DuckDuckGo and Wikipedia APIs.
- **System Telemetry:** Live CPU, RAM, and Disk resource monitoring.
- **Permission Overrides:** Users can enable/disable individual tools from Settings.

---

### Slide 6: Dedicated Study Mode
- **Pomodoro Sprint Timer:** 25m, 45m, and 60m focus blocks with circular visual countdown.
- **Rest Interval Enforcement:** Automated 5m short breaks and 15m long breaks.
- **Study Tasks & Analytics:** Integrated task checklist, session completion logging, and subject distribution charts.

---

### Slide 7: Coding Mode & Error Diagnostics
- **Automated Exception Parser:** Analyzes runtime errors (IndexError, TypeError, KeyError, RecursionError, etc.).
- **Structured Explanations:**
  1. Plain English Meaning
  2. Root Cause
  3. Step-by-Step Fix
  4. Defensively Corrected Code Example
- **Multi-Language Support:** Python, C, C++, JavaScript, HTML/CSS.

---

### Slide 8: Productivity Suite & Controlled Memory
- **Task Board:** Filter by All / Pending / Completed with due dates.
- **Searchable Notes & Voice Dictation:** Real-time keyword filtering and direct microphone voice-to-note recording.
- **Scheduled Reminders:** Target timestamp alerts.
- **Controlled Memory:** Zero secret tracking; users explicitly teach facts and can inspect or clear all memory anytime.

---

### Slide 9: Live Demo Workflow
- **Step 1:** User logs in and opens futuristic glassmorphic dashboard.
- **Step 2:** User clicks microphone $\rightarrow$ *"Sadie, start study mode."* $\rightarrow$ Study timer activates.
- **Step 3:** User asks $\rightarrow$ *"Explain Python recursion."* $\rightarrow$ Sadie explains and speaks the answer.
- **Step 4:** User says $\rightarrow$ *"Open calculator."* and *"Open my Python project."* $\rightarrow$ Tools launch safely.
- **Step 5:** User dictates note $\rightarrow$ *"Create a note: Study recursion tonight."* $\rightarrow$ Saved to DB.

---

### Slide 10: Testing, Conclusion & Future Roadmap
- **Testing Results:** 54 passing automated tests with 100% pass rate.
- **PBL Takeaway:** Successfully engineered a secure, voice-enabled AI assistant for desktop productivity.
- **Future Roadmap:** Local Whisper offline models, mobile companion app, and native VS Code extension.
