@echo off
echo ============================================================
echo YouTube Token Refresh Helper
echo ============================================================
echo.
echo This will:
echo 1. Open your browser for YouTube authentication
echo 2. Generate a new token.json
echo 3. Encode it for Railway deployment
echo.
echo Make sure client_secret.json is in this folder!
echo.
pause

python refresh_youtube_token.py

echo.
echo ============================================================
pause
