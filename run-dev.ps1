$ErrorActionPreference = "Stop"

Write-Host "Starting AI PPT Slide Generator..."

function Get-CompatiblePython {
  $candidates = @("3.12", "3.11", "3.10")
  foreach ($version in $candidates) {
    try {
      $path = (& py -$version -c "import sys; print(sys.executable)" 2>$null)
      if ($LASTEXITCODE -eq 0 -and $path) {
        return @{ Command = "py"; Args = @("-$version"); Version = $version }
      }
    } catch {}
  }

  throw "Python 3.10, 3.11, or 3.12 is required. Python 3.14 is not recommended for these pinned backend dependencies yet."
}

$python = Get-CompatiblePython

if (-not (Test-Path "backend\.venv")) {
  Write-Host "Creating backend virtual environment with Python $($python.Version)..."
  & $python.Command @($python.Args + @("-m", "venv", "backend\.venv"))
}

$venvVersion = (& backend\.venv\Scripts\python.exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ($venvVersion -notin @("3.10", "3.11", "3.12")) {
  throw "backend\.venv uses Python $venvVersion. Delete backend\.venv and rerun this script to recreate it with Python 3.10-3.12."
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
