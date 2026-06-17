from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ytdlp_webui.api.deps import file_service
from ytdlp_webui.core.schemas import FileInfo
from ytdlp_webui.services.file_service import FileService

router = APIRouter()
FileServiceDep = Annotated[FileService, Depends(file_service)]


@router.get("/files", response_model=list[FileInfo])
async def get_files(files: FileServiceDep) -> list[FileInfo]:
    return files.list_files()
