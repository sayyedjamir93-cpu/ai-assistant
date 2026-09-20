# SADIE: Speech & AI Desktop Intelligent Entity
## Comprehensive Project-Based Learning (PBL) Academic Project Report

**Project Title:** SADIE — Voice-Enabled AI Personal Assistant for Academic Productivity  
**Domain:** Artificial Intelligence, Natural Language Processing, Full-Stack Web Development, Desktop Automation  
**Team Size:** 5 Members  

---

## 1. Project Abstract
Modern computer productivity and academic learning environments require students to constantly switch contexts between web browsers, code editors, file directories, timers, and note-taking apps. Conventional AI chatbots operate strictly within text boxes and lack the ability to safely interact with desktop software, track structured study sessions, or diagnose programming errors with root causes and fixes.

**SADIE** (*Speech & AI Desktop Intelligent Entity*) is a voice-enabled, tool-augmented desktop AI personal assistant engineered specifically for students, developers, and computer productivity. Sadie bridges the gap between natural language voice interaction and operating system automation. Operating with a strict security sandbox that prohibits arbitrary shell command execution, Sadie can launch allowlisted applications, explore authorized project folders, conduct web searches, manage Pomodoro study sessions, provide programming error diagnostics, maintain voice-dictated notes, and store user-controlled memories.

---

## 2. Problem Statement
1. **Context Fragmentation:** Students waste significant cognitive focus juggling multiple disconnected utilities (pomodoro timers, calculators, file explorers, scratchpads, and browser search tabs).
2. **Passive Chatbots:** Existing AI conversational models are purely text-based and cannot interface with desktop environments or perform safe local automation.
3. **Security Vulnerabilities:** Naive attempts at desktop AI often grant unrestricted terminal or shell execution privileges to LLMs, exposing systems to dangerous command injection and data loss.
4. **Lack of Tailored Student Modes:** Generalist assistants lack dedicated study modes (Pomodoro timers, break enforcement, subject analytics) and structured programming debugging guidance.

---

## 3. Objectives & Scope

### 3.1 Objectives
- Build an end-to-end voice assistant loop: `Speech-to-Text → AI Intent Engine → Security Gatekeeper → Tool Execution → Response Generation → Text-to-Speech`.
- Implement a sandboxed tool framework with zero arbitrary command execution and explicit user permissions.
- Develop a dedicated **Study Mode** featuring subject tracking, Pomodoro timers, study tasks, and focus analytics.
- Develop a **Coding Mode** providing error diagnostics (meaning, cause, fix, corrected code), concept explanations, and code reviews.
- Provide a full productivity suite: searchable notes, task checklist, scheduled reminders, and transparent user memory.
- Design a modern futuristic glassmorphic user interface in React with real-time audio visualizer.

### 3.2 Scope
- **Target Audience:** College students, software engineering learners, and knowledge workers.
- **Operating Environment:** Windows desktop environment with cross-platform compatible architecture.
- **Security Scope:** Allowlisted applications (`calc.exe`, `notepad.exe`, `code`, `chrome`) and directories (`Documents`, `Projects`, `Study Materials`).

---

## 4. Software Requirements Specification (SRS)

### 4.1 Functional Requirements (FR)
- **FR-01 (Voice Pipeline):** The system must accept microphone voice inputs, transcribe them into text, and synthesize vocal responses in MP3 audio format.
- **FR-02 (Intent Classification):** The AI brain must classify user queries into 15 distinct intent categories and extract required parameters.
- **FR-03 (Tool Security Check):** All tool invocations must pass allowlist validation and individual user permission checks stored in the database.
- **FR-04 (Study Mode):** The system must manage timed study intervals, enforce short/long breaks, track completed tasks, and compute study analytics.
- **FR-05 (Coding Mode):** The system must diagnose programming errors across Python, C, C++, JavaScript, and HTML/CSS.
- **FR-06 (Productivity Suite):** The system must provide CRUD operations for tasks, searchable notes with voice dictation, scheduled reminders, and controlled memory.
- **FR-07 (Authentication):** The system must support JWT-based user registration, login, and isolated user data tenancy.

### 4.2 Non-Functional Requirements (NFR)
- **NFR-01 (Security):** Zero arbitrary shell execution. Strict input validation, path containment, and salted password hashing with bcrypt.
- **NFR-02 (Performance):** Intent detection response time < 50ms offline; API endpoint response time < 150ms.
- **NFR-03 (Reliability):** Comprehensive error recovery; invalid tool calls or corrupt audio payloads must never crash the backend process.
- **NFR-04 (Usability):** Dark futuristic interface with responsive design, glassmorphism, and accessibility.

---

## 5. Five-Member Team Module Allocation

| Team Member | Module & Responsibilities | Core Files Owned |
|---|---|---|
| **Member 1 (Frontend Lead)** | Futuristic React UI, Glassmorphism, Theme Tokens, Voice Visualizer, Responsive Dashboard & Pages | `frontend/src/index.css`, `frontend/src/components/*`, `frontend/src/pages/*` |
| **Member 2 (Voice & Audio Lead)** | Speech-to-Text, Text-to-Speech Engine, Markdown Audio Sanitizer, Audio Stream Endpoints | `backend/voice/speech_to_text.py`, `backend/voice/text_to_speech.py`, `backend/api/voice.py` |
| **Member 3 (AI Brain & NLP Lead)** | Intent Engine, System Prompts, Multi-Provider LLM Integration, Fallback Knowledge Base, Coding Mode | `backend/ai/brain.py`, `backend/ai/intent.py`, `backend/ai/prompts.py`, `backend/api/coding.py` |
| **Member 4 (Automation & Tools Lead)** | Sandboxed App Launcher, Folder Explorer, Web Search, Timer Engine, Hardware Telemetry | `backend/tools/*`, `backend/ai/tool_router.py`, `backend/api/tools_api.py` |
| **Member 5 (Backend, Auth & Database Lead)** | FastAPI Core, SQLAlchemy Models, SQLite DB, JWT Auth, Productivity APIs, Automated Test Suites | `backend/database/*`, `backend/api/auth.py`, `backend/api/tasks.py`, `backend/tests/*` |

---

## 6. Testing & Quality Assurance Summary

The project is verified with **54 automated unit, integration, and security test cases** passing with 100% success:
- **Health & Core:** `test_health.py` (2 tests)
- **Authentication:** `test_auth.py` (6 tests)
- **AI Brain & NLP:** `test_ai_brain.py` (12 tests)
- **Desktop Tools:** `test_tools.py` (11 tests)
- **Voice System:** `test_voice.py` (6 tests)
- **Productivity Suite:** `test_productivity.py` (4 tests)
- **Study Mode:** `test_study.py` (2 tests)
- **Coding Assistant:** `test_coding.py` (5 tests)
- **PBL Demo Integration:** `test_integration.py` (1 end-to-end test)
- **Security Hardening:** `test_security_edge_cases.py` (5 tests)

---

## 7. Conclusion & Future Scope
SADIE demonstrates that an AI assistant can be both powerful and securely contained. By replacing arbitrary command execution with a structured, allowlisted tool framework and integrating dedicated study and coding modes, Sadie provides a functional, demo-ready solution for academic productivity.

**Future Scope:**
- Integration with local Whisper fine-tuned models for offline multilingual voice recognition.
- Native mobile companion application for study notifications.
- VS Code extension integration for direct in-editor diagnostic synchronization.
