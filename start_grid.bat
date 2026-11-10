@echo off
setlocal enabledelayedexpansion

title DaeMon Grid - Master Controller

echo ===================================================
echo            DAEMON GRID - STARTUP SCRIPT
echo ===================================================

:: Ensure working directory is always repository root
cd /d "%~dp0"

:: 1. Detect and Activate Python Virtual Environment
set "VENV_ACTIVATE="
if exist "%~dp0venv\Scripts\activate.bat" (
    set "VENV_ACTIVATE=%~dp0venv\Scripts\activate.bat"
    echo [OK] Found root virtual environment: venv\
) else if exist "%~dp0orchestrator\venv\Scripts\activate.bat" (
    set "VENV_ACTIVATE=%~dp0orchestrator\venv\Scripts\activate.bat"
    echo [OK] Found orchestrator virtual environment: orchestrator\venv\
)

if defined VENV_ACTIVATE (
    echo [..] Activating Python Virtual Environment...
    call "%VENV_ACTIVATE%"
    echo [OK] Virtual Environment Activated successfully.
) else (
    echo [WARNING] No virtual environment found in .\venv or .\orchestrator\venv!
    echo [WARNING] Running with system default Python.
)

:: 2. Boot Docker Infrastructure
echo.
echo ===================================================
echo [1/4] Starting Docker Infrastructure (RabbitMQ, Redis, MinIO, Mongo)...
echo ===================================================
docker-compose up -d

:: 3. Start FastAPI Orchestrator Backend
echo.
echo ===================================================
echo [2/4] Starting FastAPI Orchestrator (Backend on 0.0.0.0:8000)...
echo ===================================================
if defined VENV_ACTIVATE (
    start "DaeMon Orchestrator" cmd /k "cd /d "%~dp0orchestrator" && call "%VENV_ACTIVATE%" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) else (
    start "DaeMon Orchestrator" cmd /k "cd /d "%~dp0orchestrator" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
)

:: 4. Start Next.js Dashboard Frontend
echo.
echo ===================================================
echo [3/3] Starting Next.js Dashboard (Frontend on port 5555)...
echo ===================================================
start "DaeMon Dashboard" cmd /k "cd /d "%~dp0dashboard" && npm run dev -- -p 5555"

:: 5. Health wait and browser launch
echo.
echo Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul 2>nul || ping -n 11 127.0.0.1 >nul

echo.
echo Launching Web Dashboard in browser...
start chrome "http://localhost:5555" 2>nul || start "" "http://localhost:5555"

echo.
echo ===================================================
echo  DaeMon Grid is now LIVE!
echo  - Dashboard:    http://localhost:5555
echo  - Orchestrator: http://localhost:8000/docs
echo  - RabbitMQ:     http://localhost:15672 (guest/guest)
echo  - MinIO:        http://localhost:9091 (Gaurav/password123)
echo.
echo  To start a worker node and process tasks, run:
echo    start_worker.bat
echo ===================================================
echo You may minimize this console.
