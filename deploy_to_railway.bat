@echo off
echo.
echo ========================================
echo   Railway Deployment Helper
echo ========================================
echo.
echo This script will help you deploy to Railway.
echo.
echo Prerequisites:
echo   1. Railway account (https://railway.app)
echo   2. Railway CLI installed
echo.
echo ========================================
echo.

echo Step 1: Install Railway CLI
echo.
echo Run this command in PowerShell (as Admin):
echo   npm install -g @railway/cli
echo.
echo Or download from: https://docs.railway.app/develop/cli
echo.
pause

echo.
echo Step 2: Login to Railway
echo.
railway login
echo.
pause

echo.
echo Step 3: Initialize Railway Project
echo.
railway init
echo.
pause

echo.
echo Step 4: Set Environment Variables
echo.
echo You need to set these variables in Railway Dashboard:
echo   - HOST=0.0.0.0
echo   - PORT=$PORT
echo   - DEBUG=false
echo   - DATABASE_URL=sqlite+aiosqlite:///./cpa_server.db
echo   - SECRET_KEY=<random-string>
echo   - CORS_ORIGINS=["https://your-lovable-app.lovable.app"]
echo.
echo Open Railway Dashboard now? (Y/N)
set /p open_dashboard=
if /i "%open_dashboard%"=="Y" start https://railway.app/dashboard
echo.
pause

echo.
echo Step 5: Deploy to Railway
echo.
railway up
echo.
pause

echo.
echo Step 6: Seed Database (Create Admin Token)
echo.
railway run poetry run python server/db/seed.py
echo.
echo IMPORTANT: Copy the Admin Token!
echo.
pause

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Copy your Railway URL
echo   2. Test: https://your-app.railway.app/health
echo   3. View docs: https://your-app.railway.app/docs
echo   4. Use Admin Token in Lovable UI
echo.
pause

