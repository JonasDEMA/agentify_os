@echo off
echo.
echo ========================================
echo   Starting CPA Server...
echo ========================================
echo.
echo Server will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo.

poetry run python -m server.main

pause

