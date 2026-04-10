@echo off
title TikTok to YouTube - Auto Downloader
color 0A
cd /d "%~dp0"

echo ============================================================
echo   TikTok to YouTube - Auto Downloader
echo ============================================================
echo.
echo This script will run FOREVER and auto-restart on errors.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not installed!
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/2] Installing packages (requirements.txt)...
python -m pip install -r requirements.txt >nul 2>&1
echo [2/2] Starting monitor...
echo.

:loop
python tiktok_to_youtube.py
echo.
echo [%time%] Restarting in 10 seconds... (Press Ctrl+C to stop)
timeout /t 10 /nobreak >nul
goto loop
