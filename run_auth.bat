@echo off
cls
echo ============================================================
echo YouTube Authentication Script
echo ============================================================
echo.
echo This will:
echo 1. Open your browser for YouTube authentication
echo 2. Generate token.json
echo 3. Encode credentials for Railway
echo.
echo Make sure you're ready to sign in with your Google account!
echo.
pause
echo.
echo Starting authentication...
echo.

python refresh_youtube_token.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo ERROR: Script failed to run
    echo ============================================================
    echo.
    echo Trying alternative Python command...
    echo.
    python3 refresh_youtube_token.py
)

echo.
echo ============================================================
echo.
pause
