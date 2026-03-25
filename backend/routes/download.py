from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..models.job import JobState
from ..schemas.api import JobResponse
from ..services.job_store import job_store
from ..utils.auth import require_token

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/download/{job_id}", dependencies=[Depends(require_token)])
def download_result(job_id: str) -> FileResponse:
    job = job_store.maybe_get(job_id)
    if not job or not job.output_path:
        raise HTTPException(status_code=404, detail="Output not found")
    if job.state != JobState.COMPLETE:
        raise HTTPException(status_code=400, detail="Job not complete")

    job.add_audit("download")
    return FileResponse(job.output_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename="generated.pptx")


@router.get("/jobs/{job_id}", response_model=JobResponse, dependencies=[Depends(require_token)])
def job_status(job_id: str) -> JobResponse:
    job = job_store.maybe_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(id=job.id, state=job.state.value, error=job.error, placeholders=job.placeholders)
