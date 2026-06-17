@echo off
echo ===================================================
echo yt-dlp-webui - Starting Dev Backend
echo ===================================================
echo.
echo Running backend FastAPI server (default port: 8765) without tray or browser...
echo.

.\.venv\Scripts\python -m ytdlp_webui.launcher --no-tray --no-browser
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start backend server. Make sure you ran setup_dev.bat first.
    pause
    exit /b %errorlevel%
)
