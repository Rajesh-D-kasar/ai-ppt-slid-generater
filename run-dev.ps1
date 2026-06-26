$ErrorActionPreference = "Stop"

Write-Host "Starting AI PPT Slide Generator..."

if (-not (Test-Path "backend\.venv")) {
  Write-Host "Creating backend virtual environment..."
  py -3 -m venv backend\.venv
}

Write-Host "Installing backend dependencies..."
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

if (-not (Test-Path "frontend\node_modules")) {
  Write-Host "Installing frontend dependencies..."
  Push-Location frontend
  npm install
  Pop-Location
}

Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
