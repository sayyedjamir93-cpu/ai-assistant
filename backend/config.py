import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""
    
    # App Settings
    APP_NAME: str = "SADIE"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'sadie.db'}"

    # Authentication
    JWT_SECRET: str = "sadie_development_secret_key_change_in_production_987654321"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI Brain (For subsequent phases)
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Tool Permissions
    ALLOWED_APPS: Union[str, List[str]] = [
        "calc.exe", "notepad.exe", "code", "chrome", "spotify", "youtube",
        "mspaint.exe", "paint", "explorer.exe", "taskmgr.exe", "ms-settings:",
        "cmd.exe", "powershell.exe", "vlc.exe", "calc", "notepad", "explorer",
        "chatgpt", "google", "mail", "gmail", "email", "word", "excel",
        "powerpoint", "winword.exe", "excel.exe", "powerpnt.exe", "snippingtool.exe",
        "camera", "clock", "lock", "control.exe", "files", "file explorer"
    ]
    ALLOWED_FOLDERS: Union[str, List[str]] = ["Documents", "Downloads", "Projects", "Study Materials", "Desktop", "Music", "Videos", "Workspace"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("ALLOWED_APPS", "ALLOWED_FOLDERS", mode="before")
    @classmethod
    def assemble_list_fields(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
