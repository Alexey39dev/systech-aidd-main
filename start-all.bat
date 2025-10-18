@echo off
echo Starting Systech AI Assistant - All Services...
echo.

echo ========================================
echo Starting Backend API...
echo ========================================
start "Backend API" cmd /k "make run-api"

echo.
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Starting Frontend...
echo ========================================
start "Frontend" cmd /k "cd frontend && npx next dev"

echo.
echo ========================================
echo All services are starting...
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo Dashboard: http://localhost:3000/dashboard
echo Chat: http://localhost:3000/chat
echo API Docs: http://localhost:8000/docs
echo.
echo NOTE: If you see framer-motion errors, the app will still work with CSS animations.
echo.
echo Press any key to exit...
pause > nul
