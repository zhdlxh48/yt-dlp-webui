from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ytdlp_webui.api.deps import recorder_service
from ytdlp_webui.core.schemas import JobInfo, JobRequest
from ytdlp_webui.services.recorder_service import RecorderService

router = APIRouter()
RecorderDep = Annotated[RecorderService, Depends(recorder_service)]


@router.get("/jobs", response_model=list[JobInfo])
async def get_jobs(recorder: RecorderDep) -> list[JobInfo]:
    return await recorder.list_jobs()


@router.post("/jobs/live/start", response_model=list[JobInfo])
async def start_live(
    request: JobRequest,
    recorder: RecorderDep,
) -> list[JobInfo]:
    return await recorder.start_live(request.channel_ids)


@router.post("/jobs/download/start", response_model=JobInfo)
async def start_download(
    request: JobRequest,
    recorder: RecorderDep,
) -> JobInfo:
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    return await recorder.start_download(request.url.strip())


@router.post("/jobs/{job_id}/stop", response_model=JobInfo)
async def stop_job(
    job_id: str,
    recorder: RecorderDep,
) -> JobInfo:
    try:
        return await recorder.stop(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
