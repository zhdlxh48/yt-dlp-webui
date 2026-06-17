@echo off
echo ===================================================
echo yt-dlp-webui - Development Environment Setup
echo ===================================================

echo.
echo [1/3] Creating Python virtual environment (.venv)...
py -m venv .venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment. Make sure Python is installed and in your PATH.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Installing Python dependencies (FastAPI, PyInstaller, etc.)...
.\.venv\Scripts\python -m pip install -e ".[dev,build]"
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Installing Svelte/Vite frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies. Make sure Node.js is installed.
    cd ..
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo ===================================================
echo Setup completed successfully!
echo.
echo To start development:
echo 1. Run backend server:
echo    .\.venv\Scripts\python -m ytdlp_webui.launcher --no-tray
echo 2. Run frontend dev server (in another terminal):
echo    cd frontend ^&^& npm run dev
echo ===================================================
pause
