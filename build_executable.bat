@echo off
REM Build CPA Monitor Executable

echo ========================================
echo Building CPA Monitor Executable
echo ========================================

REM Install PyInstaller if not already installed
echo.
echo Installing PyInstaller...
poetry add --group dev pyinstaller

REM Build executable
echo.
echo Building executable...
poetry run pyinstaller build_monitor.spec --clean

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Executable location: dist\CPA_Monitor.exe
echo.
pause

