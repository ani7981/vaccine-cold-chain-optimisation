param (
    [switch]$RebuildDb,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       VAXKAVACH: Cold-Chain Intelligence System          " -ForegroundColor Yellow
Write-Host "       Building & Launching Everything from Scratch       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Database
Write-Host "[1/5] Checking Database Services (PostgreSQL + PostGIS)..." -ForegroundColor Yellow

$dbConnected = $false
try {
    $testClient = New-Object System.Net.Sockets.TcpClient
    $testClient.Connect("127.0.0.1", 5432)
    $testClient.Close()
    $dbConnected = $true
} catch {
    $dbConnected = $false
}

if (-not $dbConnected) {
    Write-Host "  Database port 5432 not open. Starting PostGIS via WSL / Podman..." -ForegroundColor Cyan
    Start-Job -ScriptBlock { wsl -d FedoraLinux-42 -u root sleep infinity } | Out-Null
    Start-Sleep -Seconds 2
    wsl -d FedoraLinux-42 -u root podman --cgroup-manager=cgroupfs start vaxkavach_db 2>$null
    if ($LASTEXITCODE -ne 0) {
        wsl -d FedoraLinux-42 -u root podman run -d --name vaxkavach_db --cgroup-manager=cgroupfs --net=host -e POSTGRES_USER=vaxkavach -e POSTGRES_PASSWORD=vaxpassword -e POSTGRES_DB=vaxkavach_db docker.io/postgis/postgis:15-3.3 2>$null
    }
}

# Wait for DB readiness
$maxRetries = 20
$retries = 0
while ($retries -lt $maxRetries) {
    try {
        $testClient = New-Object System.Net.Sockets.TcpClient
        $testClient.Connect("127.0.0.1", 5432)
        $testClient.Close()
        Write-Host "  Database is accepting connections on 127.0.0.1:5432! [OK]" -ForegroundColor Green
        break
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

# 2. Database Schema & Seed Data
Write-Host "[2/5] Initializing Database Schema & Seeding Data..." -ForegroundColor Yellow
$PythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$env:DATABASE_URL = "postgresql://vaxkavach:vaxpassword@127.0.0.1:5432/vaxkavach_db"
Push-Location "$ScriptDir\backend"
try {
    if ($RebuildDb) {
        Write-Host "  Rebuilding all database tables from models..." -ForegroundColor Cyan
        & $PythonExe -c "import sys; sys.path.insert(0, '.'); from app.core.database import engine, Base; from app.models.all import *; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
    } else {
        & $PythonExe -c "import sys; sys.path.insert(0, '.'); from app.core.database import engine, Base; from app.models.all import *; Base.metadata.create_all(bind=engine)"
    }
    Write-Host "  Running seed data generator..." -ForegroundColor Cyan
    & $PythonExe seed.py
    Write-Host "  Database successfully initialized & seeded! [OK]" -ForegroundColor Green
} finally {
    Pop-Location
}

# 3. Build & Prepare Frontend
Write-Host "[3/5] Building & Preparing Frontend Assets..." -ForegroundColor Yellow
Push-Location "$ScriptDir\frontend"
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing frontend npm packages..." -ForegroundColor Cyan
        npm install
    }
    Write-Host "  Compiling Vite production bundle..." -ForegroundColor Cyan
    npm run build
    Write-Host "  Frontend assets compiled successfully! [OK]" -ForegroundColor Green
} finally {
    Pop-Location
}

# 4. Start Backend Process
Write-Host "[4/5] Launching Backend API Server (FastAPI on Port 8001)..." -ForegroundColor Yellow
$BackendJob = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001" -WorkingDirectory "$ScriptDir\backend" -PassThru

# Wait for backend readiness
$retries = 0
while ($retries -lt 15) {
    try {
        $res = Invoke-RestMethod -Uri "http://127.0.0.1:8001/" -TimeoutSec 2
        if ($res.status -eq "ok") {
            Write-Host "  Backend API is running on http://127.0.0.1:8001 [OK]" -ForegroundColor Green
            break
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

# 5. Start Frontend Dev Server
Write-Host "[5/5] Launching Frontend Server (Vite on Port 5173)..." -ForegroundColor Yellow
$FrontendJob = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" -WorkingDirectory "$ScriptDir\frontend" -PassThru

# Wait for frontend readiness
$retries = 0
while ($retries -lt 15) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:5173/" -UseBasicParsing -TimeoutSec 2
        if ($res.StatusCode -eq 200) {
            Write-Host "  Frontend Dashboard is live on http://localhost:5173 [OK]" -ForegroundColor Green
            break
        }
    } catch {
        $retries++
        Start-Sleep -Seconds 1
    }
}

# Start Live Telemetry Simulation
Write-Host "  Starting automated cold-chain telemetry simulation..." -ForegroundColor Cyan
try {
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8001/api/simulation/start" | Out-Null
    Write-Host "  Telemetry simulation started! Active convoy stream running. [OK]" -ForegroundColor Green
} catch {
    Write-Warning "  Simulation trigger will auto-start upon UI interaction."
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "          VAXKAVACH SYSTEM IS LIVE & OPERATIONAL           " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Dashboard Home:       http://localhost:5173/" -ForegroundColor White
Write-Host "  Operational Overview: http://localhost:5173/overview" -ForegroundColor White
Write-Host "  Telemetry Map:        http://localhost:5173/map" -ForegroundColor White
Write-Host "  Shipments Directory:  http://localhost:5173/shipments" -ForegroundColor White
Write-Host "  Active Incidents:     http://localhost:5173/problems" -ForegroundColor White
Write-Host "  Reefer Fleet:         http://localhost:5173/fleet" -ForegroundColor White
Write-Host "  Technical Engine:     http://localhost:5173/technical" -ForegroundColor White
Write-Host "  Audit Trail & Ledger: http://localhost:5173/history" -ForegroundColor White
Write-Host "  Interactive API Docs: http://127.0.0.1:8001/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C to shut down all services." -ForegroundColor DarkGray

if (-not $NoBrowser) {
    Start-Process "http://localhost:5173/"
}

try {
    while ($true) {
        Start-Sleep -Seconds 2
        if ($BackendJob.HasExited) {
            Write-Warning "Backend process exited unexpectedly."
            break
        }
        if ($FrontendJob.HasExited) {
            Write-Warning "Frontend process exited unexpectedly."
            break
        }
    }
} finally {
    Write-Host "Shutting down VaxKavach services..." -ForegroundColor Yellow
    if ($BackendJob -and -not $BackendJob.HasExited) { Stop-Process -Id $BackendJob.Id -Force }
    if ($FrontendJob -and -not $FrontendJob.HasExited) { Stop-Process -Id $FrontendJob.Id -Force }
    Write-Host "All services stopped." -ForegroundColor Green
}
