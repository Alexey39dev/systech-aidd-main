@echo off
echo Starting Systech AI Assistant - Dashboard Only...
echo.

echo ========================================
echo Starting Backend API for Dashboard...
echo ========================================
start "Backend API" cmd /k "make run-api"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Starting Frontend for Dashboard...
echo ========================================
start "Frontend" cmd /k "cd frontend && pnpm run dev"

echo.
echo ========================================
echo Dashboard services are starting...
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo Dashboard: http://localhost:3000/dashboard
echo.
echo NOTE: This starts only the dashboard functionality.
echo For full dashboard + chat, use start-all.bat
echo For chat only, use start-chat.bat
echo.
echo Press any key to exit...
pause > nul
