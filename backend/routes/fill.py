from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..models.job import JobState
from ..schemas.api import FillRequest, JobResponse
from ..services.job_store import job_store
from ..services.pptx_filler import fill_pptx
from ..utils.auth import require_token
from ..utils.config import settings

router = APIRouter(prefix="/api", tags=["fill"])


@router.post("/fill/{job_id}", response_model=JobResponse, dependencies=[Depends(require_token)])
def fill_template(job_id: str, payload: FillRequest) -> JobResponse:
    job = job_store.maybe_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        job.state = JobState.GENERATING
        output_path = Path(settings.temp_dir) / job_id / "generated.pptx"
        fill_pptx(job.template_path, output_path, payload.answers, keep_unfilled=payload.keepUnfilled)
        job.output_path = output_path
        job.state = JobState.COMPLETE
        job.add_audit("generate", answers_count=len(payload.answers))
    except Exception as exc:  # noqa: BLE001
        job.state = JobState.FAILED
        job.error = str(exc)
        raise HTTPException(status_code=500, detail="Generation failed") from exc

    return JobResponse(id=job.id, state=job.state.value, placeholders=job.placeholders)
