# yt-dlp-webui

Windows tray web UI for monitoring YouTube live streams and downloading videos with yt-dlp.

## Features

- FastAPI backend with REST and WebSocket events
- Svelte/Vite/TypeScript frontend with Tailwind CSS and daisyUI
- Multi-channel live monitoring with `yt-dlp --wait-for-video`
- General URL download mode
- App-scoped tool management for yt-dlp, FFmpeg, and Deno under `%APPDATA%\yt-dlp-webui`
- Korean UI with an i18n-friendly string structure
- Windows tray launcher and browser dashboard
- GitHub Actions Windows build and tag-based release workflow

## Development

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev,build]"
cd frontend
npm install
npm run build
cd ..
.\.venv\Scripts\python -m ytdlp_webui.launcher --no-tray
```

Open `http://127.0.0.1:8765`.

## Build

```powershell
cd frontend
npm run build
cd ..
.\.venv\Scripts\pyinstaller build\LiveRecorder.spec --noconfirm
```

The onedir executable is written to `dist\LiveRecorder\LiveRecorder.exe`.

## Security note

Do not commit personal access tokens, cookies, or downloaded tool binaries. GitHub releases are created
with the workflow-provided `GITHUB_TOKEN`.

