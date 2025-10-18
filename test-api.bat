@echo off
echo Testing Systech AI Assistant API...
echo.

echo ========================================
echo Testing Backend API Health...
echo ========================================
echo Testing health endpoint...
curl -s http://localhost:8000/health
echo.
echo.

echo ========================================
echo Testing Chat API...
echo ========================================
echo Testing chat message endpoint...
curl -X POST "http://localhost:8000/api/chat/message" -H "Content-Type: application/json" -d "{\"message\":\"Hello\",\"mode\":\"normal\",\"session_id\":null}"
echo.
echo.

echo ========================================
echo Testing Stats API...
echo ========================================
echo Testing stats endpoint (day)...
curl -s "http://localhost:8000/api/stats?period=day"
echo.
echo.

echo ========================================
echo API testing completed!
echo ========================================
pause
