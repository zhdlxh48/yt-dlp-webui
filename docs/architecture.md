# Architecture

The app has three layers:

1. **Desktop launcher** starts Uvicorn, opens a browser, and owns the tray menu.
2. **FastAPI backend** manages settings, tool installation, yt-dlp jobs, files, and WebSocket events.
3. **Svelte frontend** displays status, logs, tools, jobs, files, and settings.

The backend stores mutable app data in `%APPDATA%\yt-dlp-webui`. Large recordings default to
`%USERPROFILE%\Videos\yt-dlp-webui` so users can find them easily.

## Event flow

yt-dlp stdout/stderr is read by `ProcessRunner`, converted into structured events by
`RecorderService`, then broadcast through `EventBus` to `/ws/events`.

## Tool flow

`ToolService` installs and detects app-scoped copies of yt-dlp, FFmpeg, and Deno. These paths are
used by `YtdlpCommandBuilder` and never added to global PATH.

