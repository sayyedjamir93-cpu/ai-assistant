# PowerShell Launcher for SADIE
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting SADIE AI Personal Assistant (Full System)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; uvicorn backend.main:app --reload --port 8000"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`n[OK] Backend and Frontend running!" -ForegroundColor Green
Write-Host "  -> Frontend UI: http://localhost:5173" -ForegroundColor Yellow
Write-Host "  -> Backend API: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
