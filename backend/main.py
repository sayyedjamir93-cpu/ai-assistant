import time
import sys
import psutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.database import get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize database schema on startup."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} Backend...")
    try:
        init_db()
        print("✅ Database tables verified and initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}", file=sys.stderr)
    yield
    # Shutdown
    print(f"🛑 Shutting down {settings.APP_NAME} Backend.")


app = FastAPI(
    title=f"{settings.APP_NAME} - AI Personal Assistant API",
    version=settings.APP_VERSION,
    description="Backend API powering SADIE (Speech & AI Desktop Intelligent Entity)",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API Routers
from backend.api import auth, assistant, tools_api, voice, tasks, notes, reminders, memory, study, coding, contacts, messages_api
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(assistant.router, prefix=settings.API_PREFIX)
app.include_router(tools_api.router, prefix=settings.API_PREFIX)
app.include_router(tools_api.system_router, prefix=settings.API_PREFIX)
app.include_router(voice.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(notes.router, prefix=settings.API_PREFIX)
app.include_router(reminders.router, prefix=settings.API_PREFIX)
app.include_router(memory.router, prefix=settings.API_PREFIX)
app.include_router(study.router, prefix=settings.API_PREFIX)
app.include_router(coding.router, prefix=settings.API_PREFIX)
app.include_router(contacts.router, prefix=settings.API_PREFIX)
app.include_router(messages_api.router, prefix=settings.API_PREFIX)










@app.get("/", tags=["General"])
def root():
    """Root endpoint returning basic welcome information."""
    return {
        "app": settings.APP_NAME,
        "name": "SADIE — AI Personal Assistant",
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }


@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check including database and system metrics."""
    # Test DB connection
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "database": {
            "status": db_status,
            "engine": "SQLite" if "sqlite" in settings.DATABASE_URL else "SQLAlchemy"
        },
        "system": {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "available_memory_mb": round(memory.available / (1024 * 1024), 2)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
