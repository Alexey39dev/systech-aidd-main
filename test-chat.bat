@echo off
echo Testing Systech AI Assistant Chat...

echo.
echo Testing Backend API...
curl -s http://localhost:8000/health
echo.

echo.
echo Testing Chat API...
curl -s -X POST http://localhost:8000/api/chat/message -H "Content-Type: application/json" -d "{\"message\": \"Hello\", \"mode\": \"normal\"}"
echo.

echo.
echo Testing Frontend...
curl -s -I http://localhost:3000/chat
echo.

echo.
echo All tests completed!
pause
