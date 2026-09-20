# SADIE — System Architecture & UML Diagrams

---

## 1. System Architecture Diagram

```mermaid
graph TD
    User["👤 User (Microphone / UI)"] --> Frontend["🖥️ React + Vite Frontend (Glassmorphic UI)"]
    
    subgraph Frontend_Layer["Frontend Layer"]
        Frontend --> Visualizer["Voice Visualizer & Orb"]
        Frontend --> Dashboards["Study, Coding, Tasks, Notes Pages"]
        Frontend --> APIClient["API Client (services/api.js)"]
    end

    APIClient -->|REST / JWT Auth| FastAPI["⚡ FastAPI Backend Engine (Port 8000)"]

    subgraph Backend_Layer["Backend Application Layer"]
        FastAPI --> STT["🎙️ Speech-to-Text Engine (SpeechRecognition)"]
        FastAPI --> AIBrain["🧠 AI Brain & Intent Classifier"]
        FastAPI --> TTS["🔊 Text-to-Speech Engine (gTTS)"]
        
        AIBrain --> SecurityGate["🛡️ Security & Permission Gatekeeper"]
        
        subgraph Tool_Sandboxing["Sandboxed Desktop Tools"]
            SecurityGate --> VSCodeGen["VS Code Project & Program Generator"]
            SecurityGate --> MediaCtrl["YouTube & Spotify Media Controller"]
            SecurityGate --> AppLaunch["App Launcher (calc, notepad, code, taskmgr)"]
            SecurityGate --> FolderLaunch["Folder Explorer (Projects, Study)"]
            SecurityGate --> WebSearch["Web Search Engine (DuckDuckGo / Wiki)"]
            SecurityGate --> Timers["Timer & Pomodoro Engine"]
            SecurityGate --> SysInfo["Hardware & System Telemetry"]
        end
    end

    subgraph Persistence_Layer["Database & Storage Layer"]
        FastAPI --> SQLAlchemy["ORM (SQLAlchemy 2.0)"]
        SQLAlchemy --> SQLite[("💾 SQLite Database (sadie.db)")]
    end
```

---

## 2. End-to-End Voice Interaction Flowchart

```mermaid
flowchart TD
    Start(["Start: User clicks Mic / speaks"]) --> Record["Capture Audio Input (Microphone)"]
    Record --> STT["Convert Speech to Text (STT Engine)"]
    STT --> Clean["Extract User Query Text"]
    Clean --> Intent["Intent Classification & Parameter Extraction"]
    
    Intent --> ToolCheck{"Is Tool Required?"}
    
    ToolCheck -- No --> GenAnswer["AI Brain Generates Knowledge Response"]
    ToolCheck -- Yes --> PermCheck{"Check User Permission & Allowlist"}
    
    PermCheck -- Denied --> ErrMsg["Generate Friendly Permission Error Message"]
    PermCheck -- Approved --> Exec["Execute Sandboxed Tool (App/Folder/Timer/Search)"]
    
    Exec --> FormatResult["Format Tool Execution Result"]
    FormatResult --> GenAnswer
    ErrMsg --> GenAnswer
    
    GenAnswer --> SaveDB["Save Message & Tool Call to SQLite DB"]
    SaveDB --> TTS["Synthesize Response Audio (TTS Engine)"]
    TTS --> PlayAudio["Stream Audio to Frontend & Speak"]
    PlayAudio --> Display["Render UI Response & Tool Execution Badge"]
    Display --> End(["Ready for Next Interaction"])
```

---

## 3. Data Flow Diagram (DFD Level 1)

```mermaid
graph LR
    User(["👤 User"]) -->|Voice / Text Query| Process1["1.0 Audio & Text Processing"]
    Process1 -->|Transcribed Text| Process2["2.0 Intent & NLP Reasoning"]
    
    Process2 -->|Context & Memory Request| DB[("Database: Users, Messages, Memory")]
    DB -->|History & Memory Facts| Process2
    
    Process2 -->|Tool Action & Parameters| Process3["3.0 Security & Tool Router"]
    Process3 -->|Permission Verification| DB
    Process3 -->|Approved Execution| Desktop["🖥️ Desktop OS / Subprocesses / Web"]
    Desktop -->|Execution Status| Process3
    
    Process3 -->|Tool Result| Process4["4.0 Response & Speech Synthesis"]
    Process2 -->|Direct Answer| Process4
    
    Process4 -->|Voice Audio Stream & UI Payload| User
```

---

## 4. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USER ||--o{ CONVERSATION : owns
    USER ||--o{ TASK : manages
    USER ||--o{ NOTE : creates
    USER ||--o{ REMINDER : schedules
    USER ||--o{ MEMORY : stores
    USER ||--o{ STUDY_SESSION : logs
    USER ||--o{ TOOL_PERMISSION : configures

    CONVERSATION ||--o{ MESSAGE : contains

    USER {
        int id PK
        string name
        string email
        string password_hash
        boolean is_active
        datetime created_at
    }

    CONVERSATION {
        int id PK
        int user_id FK
        string title
        datetime created_at
    }

    MESSAGE {
        int id PK
        int conversation_id FK
        string sender
        text content
        text tool_calls
        datetime created_at
    }

    TASK {
        int id PK
        int user_id FK
        string title
        text description
        datetime due_date
        boolean completed
        datetime created_at
    }

    NOTE {
        int id PK
        int user_id FK
        string title
        text content
        datetime created_at
        datetime updated_at
    }

    REMINDER {
        int id PK
        int user_id FK
        string title
        datetime remind_at
        boolean is_triggered
        datetime created_at
    }

    MEMORY {
        int id PK
        int user_id FK
        string key
        text value
        datetime created_at
    }

    STUDY_SESSION {
        int id PK
        int user_id FK
        string subject
        string task_name
        int duration_minutes
        boolean completed
        datetime created_at
    }

    TOOL_PERMISSION {
        int id PK
        int user_id FK
        string tool_name
        boolean is_allowed
        datetime created_at
    }
```
