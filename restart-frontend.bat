@echo off
echo ========================================
echo Restarting Frontend with Tailwind CSS
echo ========================================
echo.

echo Stopping any running frontend processes...
taskkill /FI "WINDOWTITLE eq Frontend*" /F 2>nul
taskkill /IM node.exe /FI "COMMANDLINE eq *next dev*" /F 2>nul
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo Installing missing dependencies...
echo ========================================
cd frontend

REM Check if pnpm exists in node_modules
if exist "node_modules\.bin\pnpm.cmd" (
    echo Using local pnpm...
    call node_modules\.bin\pnpm.cmd add -D autoprefixer postcss
    goto :start_server
)

REM Check if npm exists in node_modules
if exist "node_modules\.bin\npm.cmd" (
    echo Using local npm...
    call node_modules\.bin\npm.cmd install --save-dev autoprefixer postcss
    goto :start_server
)

REM Try global pnpm
where pnpm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using global pnpm...
    call pnpm add -D autoprefixer postcss
    goto :start_server
)

REM Try global npm
where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using global npm...
    call npm install --save-dev autoprefixer postcss
    goto :start_server
)

echo ERROR: No package manager found!
echo Please install Node.js first.
pause
exit /b 1

:start_server
echo.
echo ========================================
echo Starting Next.js dev server...
echo ========================================

REM Use local Next.js if available
if exist "node_modules\.bin\next.cmd" (
    echo Starting with local Next.js...
    start "Frontend Dev Server" cmd /k "node_modules\.bin\next.cmd dev"
    goto :done
)

REM Try pnpm
if exist "node_modules\.bin\pnpm.cmd" (
    start "Frontend Dev Server" cmd /k "node_modules\.bin\pnpm.cmd run dev"
    goto :done
)

REM Try npm
if exist "node_modules\.bin\npm.cmd" (
    start "Frontend Dev Server" cmd /k "node_modules\.bin\npm.cmd run dev"
    goto :done
)

where pnpm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "Frontend Dev Server" cmd /k "pnpm run dev"
    goto :done
)

where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "Frontend Dev Server" cmd /k "npm run dev"
    goto :done
)

:done
echo.
echo ========================================
echo Frontend is restarting...
echo ========================================
echo.
echo Open: http://localhost:3000/dashboard
echo.
echo Wait 10-15 seconds for compilation to finish
echo.
cd ..
pause
