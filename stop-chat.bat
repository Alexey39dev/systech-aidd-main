@echo off
echo Stopping Systech AI Assistant - Chat Services...
echo.

echo ========================================
echo Stopping Frontend (port 3000)...
echo ========================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Stopping process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo ========================================
echo Stopping Backend API (port 8000)...
echo ========================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo ========================================
echo Chat services stopped successfully!
echo ========================================
echo.
echo NOTE: This stops only the chat services.
echo For stopping all services, use stop-all.bat
echo.
pause