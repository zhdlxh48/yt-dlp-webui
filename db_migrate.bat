@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo yt-dlp-webui - Database Migration Tool
echo ===================================================
echo.

set ACTION=%1
set MSG=%2

if "%ACTION%"=="" (
    echo Usage:
    echo   db_migrate.bat init                 - Install alembic and initialize migration setup
    echo   db_migrate.bat generate "message"   - Detect model changes and generate a migration file
    echo   db_migrate.bat upgrade              - Apply all pending migrations to the database
    echo   db_migrate.bat history              - Show migration history
    exit /b 0
)

:: Set PYTHONPATH to resolve backend modules correctly
set PYTHONPATH=%~dp0backend;%PYTHONPATH%

if "%ACTION%"=="init" (
    echo [1/3] Installing alembic...
    .\.venv\Scripts\python -m pip install alembic
    if !errorlevel! neq 0 (
        echo Error: Failed to install alembic.
        exit /b !errorlevel!
    )

    echo [2/3] Setting up Alembic files...
    .\.venv\Scripts\python scripts\setup_alembic.py
    if !errorlevel! neq 0 (
        echo Error: Failed to setup alembic structure.
        exit /b !errorlevel!
    )

    echo.
    echo Alembic has been successfully initialized and configured!
    exit /b 0
)

if "%ACTION%"=="generate" (
    if "%MSG%"=="" (
        echo Error: Please provide a migration message.
        echo Example: db_migrate.bat generate "add_users_table"
        exit /b 1
    )

    echo Generating migration file with message: %MSG%
    .\.venv\Scripts\alembic revision --autogenerate -m %MSG%
    if !errorlevel! neq 0 (
        echo Error: Failed to generate migration file.
        exit /b !errorlevel!
    )
    exit /b 0
)

if "%ACTION%"=="upgrade" (
    echo Applying pending migrations...
    .\.venv\Scripts\alembic upgrade head
    if !errorlevel! neq 0 (
        echo Error: Failed to apply migrations.
        exit /b !errorlevel!
    )
    exit /b 0
)

if "%ACTION%"=="history" (
    echo Showing migration history...
    .\.venv\Scripts\alembic history --verbose
    if !errorlevel! neq 0 (
        echo Error: Failed to fetch migration history.
        exit /b !errorlevel!
    )
    exit /b 0
)

echo Error: Unknown action "%ACTION%".
exit /b 1
