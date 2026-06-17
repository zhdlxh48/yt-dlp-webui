@echo off
echo ===================================================
echo yt-dlp-webui - Building Windows Executable (.exe)
echo ===================================================

echo.
echo [1/2] Building frontend static resources...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo Error: Frontend build failed.
    cd ..
    pause
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/2] Packaging application with PyInstaller...
if not exist .\.venv\Scripts\pyinstaller.exe (
    echo Error: PyInstaller not found in .venv. Please run setup_dev.bat first.
    pause
    exit /b 1
)
.\.venv\Scripts\pyinstaller build\LiveRecorder.spec --noconfirm
if %errorlevel% neq 0 (
    echo Error: PyInstaller packaging failed.
    pause
    exit /b %errorlevel%
)

echo.
echo ===================================================
echo Build completed successfully!
echo Executable location: dist\LiveRecorder\LiveRecorder.exe
echo ===================================================
pause
