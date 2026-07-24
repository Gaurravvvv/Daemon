@echo off
echo =========================================
echo       DAEMON GRID - STARTUP SCRIPT
echo =========================================

echo Starting Docker Infrastructure (RabbitMQ, Redis, MinIO, Mongo)...
docker-compose up -d

echo.
echo Starting FastAPI Orchestrator (Backend)...
start cmd /k "cd orchestrator && .\venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"

echo.
echo Starting Next.js Dashboard (Frontend) on port 5555...
start cmd /k "cd dashboard && npm run dev -- -p 5555"

echo.
echo Waiting 10 seconds for services to boot up...
timeout /t 10 /nobreak >nul

echo.
echo Launching Google Chrome...
start chrome "http://localhost:5555"

echo.
echo Startup complete! You can minimize this window.
