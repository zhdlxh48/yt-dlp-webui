from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from traceback import format_exc

import uvicorn

from ytdlp_webui.app import create_app
from ytdlp_webui.core.config_store import ConfigStore
from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.desktop.browser import open_dashboard


def main() -> None:
    try:
        _main()
    except Exception:
        _launcher_log(format_exc())
        raise


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-tray", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    paths = AppPaths.discover()
    _launcher_log("launcher start")
    config_store = ConfigStore(paths)
    settings = config_store.load()
    _launcher_log("settings loaded")

    server = uvicorn.Server(
        uvicorn.Config(
            create_app(),
            host=args.host,
            port=args.port,
            log_config=None,
            access_log=False,
        )
    )
    thread = threading.Thread(target=server.run, name="uvicorn", daemon=True)
    thread.start()
    _launcher_log("server thread started")
    _wait_for_server(url)
    _launcher_log("server wait finished")

    if settings.app.open_browser_on_start and not args.no_browser:
        open_dashboard(url)

    def post(path: str, body: dict[str, object] | None = None) -> None:
        data = json.dumps(body or {}).encode("utf-8")
        request = urllib.request.Request(
            f"{url}{path}",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(request, timeout=3).read()
        except OSError:
            pass

    def quit_app() -> None:
        server.should_exit = True

    if args.no_tray:
        try:
            while thread.is_alive():
                time.sleep(0.3)
        except KeyboardInterrupt:
            quit_app()
    else:
        from ytdlp_webui.desktop.tray import TrayApp

        tray = TrayApp(
            open_dashboard=lambda: open_dashboard(url),
            start_monitoring=lambda: post("/api/jobs/live/start", {}),
            stop_all=lambda: [post(f"/api/jobs/{job['id']}/stop") for job in _jobs(url)],
            quit_app=quit_app,
        )
        tray.run()

    thread.join(timeout=10)


def _wait_for_server(url: str) -> None:
    for _ in range(60):
        try:
            urllib.request.urlopen(f"{url}/api/health", timeout=1).read()
            return
        except OSError:
            time.sleep(0.2)


def _jobs(url: str) -> list[dict[str, object]]:
    try:
        with urllib.request.urlopen(f"{url}/api/jobs", timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))
    except OSError:
        return []


def _launcher_log(message: str) -> None:
    log_dir = Path.home() / "AppData" / "Roaming" / "yt-dlp-webui" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    with (log_dir / "launcher.log").open("a", encoding="utf-8") as log:
        log.write(f"{timestamp} {message}\n")


if __name__ == "__main__":
    main()
