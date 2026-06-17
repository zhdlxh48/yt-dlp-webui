from __future__ import annotations

import asyncio
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from ytdlp_webui.core.event_bus import EventBus
from ytdlp_webui.core.paths import AppPaths
from ytdlp_webui.core.schemas import ToolInfo, ToolStatus

YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
DENO_URL = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"


class ToolService:
    def __init__(self, paths: AppPaths, events: EventBus) -> None:
        self.paths = paths
        self.events = events

    async def status(self) -> ToolStatus:
        tools = [
            ToolInfo(
                name="yt-dlp",
                installed=self.yt_dlp_path.exists(),
                path=str(self.yt_dlp_path),
            ),
            ToolInfo(
                name="ffmpeg",
                installed=self.ffmpeg_path.exists(),
                path=str(self.ffmpeg_path),
            ),
            ToolInfo(name="deno", installed=self.deno_path.exists(), path=str(self.deno_path)),
        ]
        enriched = [await self._with_version(tool) for tool in tools]
        return ToolStatus(tools=enriched)

    async def install_missing(self) -> ToolStatus:
        await self.events.publish("tools.status", {"message": "도구 설치 상태를 확인합니다."})
        if not self.yt_dlp_path.exists():
            await self._download_file(YTDLP_URL, self.yt_dlp_path, "yt-dlp")
        if not self.ffmpeg_path.exists():
            await self._download_ffmpeg()
        if not self.deno_path.exists():
            await self._download_deno()
        status = await self.status()
        await self.events.publish("tools.status", status.model_dump())
        return status

    @property
    def yt_dlp_path(self) -> Path:
        return self.paths.tools / "yt-dlp" / "yt-dlp.exe"

    @property
    def ffmpeg_path(self) -> Path:
        return self.paths.tools / "ffmpeg" / "ffmpeg.exe"

    @property
    def deno_path(self) -> Path:
        return self.paths.tools / "deno" / "deno.exe"

    async def _with_version(self, tool: ToolInfo) -> ToolInfo:
        if not tool.installed:
            return tool
        version = await asyncio.to_thread(self._read_version, tool.path)
        return tool.model_copy(update={"version": version})

    def _read_version(self, path: str) -> str:
        try:
            result = subprocess.run(
                [path, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            first = (result.stdout or result.stderr).splitlines()[0]
            return first.strip()
        except (OSError, subprocess.SubprocessError, IndexError):
            return ""

    async def _download_file(self, url: str, destination: Path, label: str) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        await self.events.publish("tools.status", {"message": f"{label} 다운로드 중"})
        await asyncio.to_thread(urllib.request.urlretrieve, url, destination)

    async def _download_ffmpeg(self) -> None:
        await self.events.publish("tools.status", {"message": "FFmpeg 다운로드 중"})
        zip_path = self.paths.tools / "ffmpeg" / "ffmpeg.zip"
        await asyncio.to_thread(urllib.request.urlretrieve, FFMPEG_URL, zip_path)
        await asyncio.to_thread(self._extract_named_tools, zip_path, self.paths.tools / "ffmpeg")
        zip_path.unlink(missing_ok=True)

    async def _download_deno(self) -> None:
        await self.events.publish("tools.status", {"message": "Deno 다운로드 중"})
        zip_path = self.paths.tools / "deno" / "deno.zip"
        await asyncio.to_thread(urllib.request.urlretrieve, DENO_URL, zip_path)
        await asyncio.to_thread(self._extract_named_tools, zip_path, self.paths.tools / "deno")
        zip_path.unlink(missing_ok=True)

    def _extract_named_tools(self, zip_path: Path, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.namelist():
                name = Path(member).name.lower()
                if name in {"ffmpeg.exe", "ffprobe.exe", "deno.exe"}:
                    source = archive.open(member)
                    target = destination / Path(member).name
                    with source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
