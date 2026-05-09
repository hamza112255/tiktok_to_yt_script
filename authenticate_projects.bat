@echo off
echo ========================================
echo YouTube API Projects Authentication
echo ========================================
echo.
echo This will authenticate all your YouTube API projects.
echo Make sure you have created:
echo   - client_secret_1.json
echo   - client_secret_2.json
echo   - client_secret_3.json
echo.
pause
echo.

python authenticate_all_projects.py

echo.
echo ========================================
echo.
pause
