from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from ytdlp_webui.api.deps import tool_service
from ytdlp_webui.core.schemas import ToolStatus
from ytdlp_webui.services.tool_service import ToolService

router = APIRouter()
ToolServiceDep = Annotated[ToolService, Depends(tool_service)]


@router.get("/tools", response_model=ToolStatus)
async def get_tools(tools: ToolServiceDep) -> ToolStatus:
    return await tools.status()


@router.post("/tools/install", response_model=ToolStatus)
async def install_tools(tools: ToolServiceDep) -> ToolStatus:
    return await tools.install_missing()
