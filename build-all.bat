@echo off
echo Building Systech AI Assistant - All Services...
echo.

echo ========================================
echo Building Backend (Python)...
echo ========================================
echo Installing Python dependencies...
uv pip install -e .
uv pip install -e ".[dev]"

echo.
echo ========================================
echo Building Frontend (Next.js)...
echo ========================================
echo Installing frontend dependencies...
cd frontend
call pnpm install

echo.
echo Building frontend for production...
call pnpm run build

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo To start all services, run: start-all.bat
echo To start only chat, run: start-chat.bat
echo.
pause
