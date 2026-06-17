# AGENTS.md

## Project

`yt-dlp-webui` is a Windows-first tray application. It starts a FastAPI backend, serves a
Svelte/Vite frontend, and controls yt-dlp jobs through subprocesses.

## Non-negotiables

- Never use, store, log, or commit personal access tokens.
- Do not bundle yt-dlp, FFmpeg, or Deno in git. Download them into `%APPDATA%\yt-dlp-webui\tools`.
- Do not modify global Python packages. Use repo-local `.venv` or CI-managed environments.
- Use subprocess argument lists, never shell command strings, for yt-dlp execution.
- Keep modules single-purpose. Prefer small services and routers over large mixed files.

## Architecture

- Backend package: `backend/ytdlp_webui`
- Frontend app: `frontend`
- Runtime app data: `%APPDATA%\yt-dlp-webui`
- Default downloads: `%USERPROFILE%\Videos\yt-dlp-webui`
- Windows package: PyInstaller onedir, `LiveRecorder.exe`

## Verification

Run these before committing:

```powershell
.\.venv\Scripts\python -m ruff check backend tests
.\.venv\Scripts\python -m pytest
cd frontend
npm run build
```

## Release

Push a tag like `v0.1.0`. GitHub Actions builds the Windows zip and uploads it to a GitHub Release.

