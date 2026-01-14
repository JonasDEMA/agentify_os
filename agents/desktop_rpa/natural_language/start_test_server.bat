@echo off
echo.
echo ========================================
echo   CPA Agent - Natural Language Test
echo ========================================
echo.
echo Starting WebSocket server...
echo.
echo After the server starts:
echo 1. Open test_ui.html in your browser
echo 2. Type natural language commands
echo 3. Watch the agent respond in real-time
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

cd /d "%~dp0..\..\..\"
poetry run python -m agents.desktop_rpa.natural_language.websocket_server

pause

