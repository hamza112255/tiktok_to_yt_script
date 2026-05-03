@echo off
echo ============================================================
echo Installing Instagram to YouTube Downloader
echo ============================================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Installing required packages...
echo Trying pip...
pip install instaloader google-auth google-auth-oauthlib google-api-python-client 2>nul
if errorlevel 1 (
    echo pip not found, trying python -m pip...
    python -m pip install instaloader google-auth google-auth-oauthlib google-api-python-client
    if errorlevel 1 (
        echo ERROR: Could not install packages!
        echo Please run manually: python -m pip install instaloader google-auth google-auth-oauthlib google-api-python-client
        pause
        exit /b 1
    )
)
echo.

echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found!
    echo Please install FFmpeg - see INSTALL_FFMPEG_WINDOWS.txt
    echo.
) else (
    echo FFmpeg is installed!
    echo.
)

echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Edit instagram_youtube_local.py with your credentials
echo 2. Make sure you have client_secret.json and token.json
echo 3. Run: run_local.bat
echo.

pause
