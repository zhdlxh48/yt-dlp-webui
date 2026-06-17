@echo off
echo ===================================================
echo yt-dlp-webui - Starting Dev Frontend (Vite)
echo ===================================================
echo.
echo Running frontend development server with HMR...
echo.

cd frontend
call npm run dev
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start frontend dev server. Make sure Node.js is installed.
    cd ..
    pause
    exit /b %errorlevel%
)
cd ..
