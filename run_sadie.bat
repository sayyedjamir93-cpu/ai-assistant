@echo off
TITLE SADIE — AI Personal Assistant Launcher
echo ========================================================
echo   Starting SADIE AI Personal Assistant (Full System)
echo ========================================================

REM Activate virtual environment and start FastAPI Backend in new window (0.0.0.0 allows phones to connect)
start "SADIE Backend API (Port 8000)" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait 2 seconds for backend to start
timeout /t 2 /nobreak >nul

REM Start Vite React Frontend
start "SADIE Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev -- --host"

echo.
echo [OK] Both Backend and Frontend services launched!
echo - Backend API: http://127.0.0.1:8000/docs
echo - Frontend UI: http://localhost:5173/
echo.
pause
