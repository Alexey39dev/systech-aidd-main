@echo off
echo Starting Systech AI Assistant - Chat Only...
echo.

echo ========================================
echo Starting Backend API for Chat...
echo ========================================
start "Backend API" cmd /k "make run-api"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Starting Frontend for Chat...
echo ========================================
start "Frontend" cmd /k "cd frontend && npx next dev"

echo.
echo ========================================
echo Chat services are starting...
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo Chat: http://localhost:3000/chat
echo.
echo NOTE: This starts only the chat functionality.
echo For full dashboard + chat, use start-all.bat
echo.
echo Press any key to exit...
pause > nul