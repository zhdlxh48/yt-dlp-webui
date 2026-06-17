from __future__ import annotations

import asyncio
import sys
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from ytdlp_webui.api.deps import tool_service
from ytdlp_webui.core.schemas import ToolStatus
from ytdlp_webui.services.tool_service import ToolService

router = APIRouter()
ToolServiceDep = Annotated[ToolService, Depends(tool_service)]


@router.get("/tools", response_model=ToolStatus)
async def get_tools(tools: ToolServiceDep) -> ToolStatus:
    return await tools.status()


@router.post("/tools/install", response_model=ToolStatus)
async def install_tools(tools: ToolServiceDep, force: bool = False) -> ToolStatus:
    try:
        return await tools.install_missing(force=force)
    except PermissionError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                "도구 파일이 현재 실행 중이거나 사용 중이어서 설치할 수 없습니다. "
                "실행 중인 감시 작업을 정지한 후 다시 시도해 주세요."
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"도구 설치 중 에러가 발생했습니다: {exc}",
        ) from exc


@router.post("/tools/open-folder")
async def open_tools_folder(tools: ToolServiceDep) -> Response:
    if sys.platform == "win32":
        folder = tools.paths.tools
        await asyncio.create_subprocess_exec("explorer.exe", str(folder.resolve()))
    return Response(status_code=204)
