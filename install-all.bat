@echo off
echo Installing Systech AI Assistant - All Dependencies...
echo.

echo ========================================
echo Installing Backend Dependencies...
echo ========================================
echo Installing Python dependencies with uv...
uv pip install -e .
uv pip install -e ".[dev]"

echo.
echo ========================================
echo Installing Frontend Dependencies...
echo ========================================
echo Installing frontend dependencies with pnpm...
cd frontend
call pnpm install

echo.
echo ========================================
echo All dependencies installed successfully!
echo ========================================
echo.
echo To start all services, run: start-all.bat
echo To build for production, run: build-all.bat
echo.
pause
