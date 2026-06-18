from __future__ import annotations

from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class AppConfig(BaseModel):
    language: str = "ko"
    open_browser_on_start: bool = True
    start_monitoring_on_launch: bool = True


class PathsConfig(BaseModel):
    downloads_dir: str
    app_data_dir: str = ""


class ToolsConfig(BaseModel):
    yt_dlp_path: str = ""
    ffmpeg_path: str = ""
    deno_path: str = ""
    auto_install_tools: bool = True


class LiveChannel(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str = ""
    handle: str = ""
    url: str = ""
    enabled: bool = True

    @field_validator("handle")
    @classmethod
    def handle_format(cls, value: str) -> str:
        val = value.strip()
        if val:
            if not val.startswith("@"):
                val = "@" + val
        return val

    @model_validator(mode="after")
    def set_url_from_handle(self) -> LiveChannel:
        if self.handle:
            self.url = f"https://www.youtube.com/{self.handle}/live"
        if not self.handle and not self.url.strip():
            raise ValueError("Either Handle or URL is required")
        return self


class RetryConfig(BaseModel):
    retries: str = "infinite"
    fragment_retries: str = "infinite"
    socket_timeout: int = 30


class LiveConfig(BaseModel):
    channels: list[LiveChannel] = Field(default_factory=list)
    wait_for_video_seconds: int = 60
    live_from_start: bool = True
    retry_policy: RetryConfig = Field(default_factory=RetryConfig)


class DownloadConfig(BaseModel):
    format_selector: str = "bv*+ba/b"
    merge_output_format: str = "mp4"
    output_template: str = "%(upload_date>%Y-%m-%d)s %(title).200B [%(id)s].%(ext)s"
    extra_args: str = ""


class AuthConfig(BaseModel):
    cookies_file: str = ""


class StartupConfig(BaseModel):
    enabled: bool = False


class Settings(BaseModel):
    app: AppConfig
    paths: PathsConfig
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    live: LiveConfig = Field(default_factory=LiveConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    startup: StartupConfig = Field(default_factory=StartupConfig)


class ToolInfo(BaseModel):
    name: Literal["yt-dlp", "ffmpeg", "deno"]
    installed: bool
    path: str = ""
    version: str = ""


class ToolStatus(BaseModel):
    tools: list[ToolInfo]

    def path_for(self, name: str) -> Path | None:
        for tool in self.tools:
            if tool.name == name and tool.installed and tool.path:
                return Path(tool.path)
        return None


class JobRequest(BaseModel):
    url: str = ""
    channel_ids: list[str] = Field(default_factory=list)


class JobInfo(BaseModel):
    id: str
    kind: Literal["live", "download"]
    title: str
    status: Literal["starting", "running", "stopping", "finished", "failed", "stopped"]
    command: list[str] = Field(default_factory=list)
    started_at: str
    finished_at: str = ""
    return_code: int | None = None
    channel_id: str | None = None
    is_downloading: bool = False


class FileInfo(BaseModel):
    name: str
    path: str
    size: int
    modified_at: str

    @property
    def suffix(self) -> str:
        return Path(self.name).suffix

