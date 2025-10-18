@echo off
echo Stopping Systech AI Assistant - All Services...
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
echo Stopping alternative ports...
echo ========================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    echo Stopping process %%a on port 8001...
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Stopping process %%a on port 8002...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo ========================================
echo All services stopped successfully!
echo ========================================
pause
