@echo off
setlocal enabledelayedexpansion

title DaeMon Grid - Volunteer Worker Node

echo ===================================================
echo         DAEMON GRID - VOLUNTEER WORKER NODE
echo ===================================================

cd /d "%~dp0"

:: Detect and Activate Virtual Environment
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
    echo [OK] Virtual Environment Activated.
) else (
    echo [WARNING] No virtual environment found in .\venv or .\orchestrator\venv!
)

echo.
echo ===================================================
echo Connecting Worker to DaeMon Grid Mesh...
echo - Target Orchestrator: http://localhost:8000
echo - Target Broker:       amqp://guest:guest@localhost:5672/
echo - Target Pool:         public_pool
echo ===================================================
echo.

cd /d "%~dp0worker"
python main.py

echo.
echo Worker process terminated.
pause

