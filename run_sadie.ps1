# PowerShell Launcher for SADIE
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting SADIE AI Personal Assistant (Full System)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Start Backend (0.0.0.0 allows phones on same Wi-Fi to connect)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev -- --host"

Write-Host "`n[OK] Backend and Frontend running!" -ForegroundColor Green
Write-Host "  -> Laptop UI:    http://localhost:5173" -ForegroundColor Yellow
Write-Host "  -> Phone Access: http://192.168.0.103:5173 (on same Wi-Fi)" -ForegroundColor Cyan
Write-Host "  -> Backend API:  http://127.0.0.1:8000/docs" -ForegroundColor Gray
