@echo off
REM Calculator POC Startup Script for Windows

echo Starting Calculator POC...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo Docker is running
echo.

REM Build and start services
echo Building and starting services...
docker-compose -f docker-compose.calculator-poc.yml up --build -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Calculator POC is running!
echo.
echo Access points:
echo    - Web UI:            http://localhost:5173
echo    - Scheduler API:     http://localhost:8000
echo    - API Docs:          http://localhost:8000/docs
echo    - Calculation Agent: http://localhost:8001
echo    - Formatting Agent:  http://localhost:8002
echo.
echo Useful commands:
echo    - View logs:         docker-compose -f docker-compose.calculator-poc.yml logs -f
echo    - Stop services:     docker-compose -f docker-compose.calculator-poc.yml down
echo    - Restart services:  docker-compose -f docker-compose.calculator-poc.yml restart
echo.
echo For more information, see docs\CALCULATOR_POC.md

