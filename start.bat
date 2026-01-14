@echo off
echo.
echo ========================================
echo   Starting CPA Agent Monitor...
echo ========================================
echo.

poetry run python -m agents.desktop_rpa.ui.cpa_monitor

pause

