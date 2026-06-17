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
        self._version_cache: dict[str, str] = {}


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

    async def install_missing(self, force: bool = False) -> ToolStatus:
        await self.events.publish_log("도구 설치 상태를 확인합니다.")
        if force or not self.yt_dlp_path.exists():
            await self._download_file(YTDLP_URL, self.yt_dlp_path, "yt-dlp")
        if force or not self.ffmpeg_path.exists():
            await self._download_ffmpeg()
        if force or not self.deno_path.exists():
            await self._download_deno()
        status = await self.status()
        await self.events.publish("tools.status", status.model_dump())
        await self.events.publish_log("도구 설치 상태 확인을 완료했습니다.")
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
        if tool.path in self._version_cache:
            version = self._version_cache[tool.path]
        else:
            version = await asyncio.to_thread(self._read_version, tool.path)
            if version:
                self._version_cache[tool.path] = version
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
        loop = asyncio.get_running_loop()
        last_percent = -1

        def reporthook(block_num: int, block_size: int, total_size: int) -> None:
            nonlocal last_percent
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, int(downloaded * 100 / total_size))
                if percent != last_percent:
                    last_percent = percent
                    msg = (
                        f"{label} 다운로드 중: {percent}% "
                        f"({downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB)"
                    )
                    asyncio.run_coroutine_threadsafe(
                        self._report_download_progress(msg, label, percent),
                        loop
                    )
            else:
                msg = f"{label} 다운로드 중: {downloaded / (1024*1024):.1f}MB 수신"
                asyncio.run_coroutine_threadsafe(
                    self._report_download_progress(msg, label, -1),
                    loop
                )

        await self.events.publish_log(f"{label} 다운로드 시작: {url}")
        try:
            await asyncio.to_thread(urllib.request.urlretrieve, url, destination, reporthook)
            self._version_cache.clear()
            await self.events.publish_log(f"{label} 다운로드 완료")
        except Exception as e:
            await self.events.publish_log(f"{label} 다운로드 실패: {e}", level="error")
            raise

    async def _report_download_progress(self, message: str, label: str, percent: int) -> None:
        await self.events.publish_log(message)
        await self.events.publish("tools.status", {
            "message": message,
            "tool": label,
            "percent": percent
        })

    async def _download_ffmpeg(self) -> None:
        zip_path = self.paths.tools / "ffmpeg" / "ffmpeg.zip"
        await self._download_file(FFMPEG_URL, zip_path, "ffmpeg")
        await self.events.publish_log("ffmpeg 압축 해제 중...")
        await asyncio.to_thread(self._extract_named_tools, zip_path, self.paths.tools / "ffmpeg")
        zip_path.unlink(missing_ok=True)
        await self.events.publish_log("ffmpeg 압축 해제 및 설치 완료")

    async def _download_deno(self) -> None:
        zip_path = self.paths.tools / "deno" / "deno.zip"
        await self._download_file(DENO_URL, zip_path, "deno")
        await self.events.publish_log("deno 압축 해제 중...")
        await asyncio.to_thread(self._extract_named_tools, zip_path, self.paths.tools / "deno")
        zip_path.unlink(missing_ok=True)
        await self.events.publish_log("deno 압축 해제 및 설치 완료")

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
