from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.job import JobState
from ..schemas.api import ParseResponse
from ..services.job_store import job_store
from ..services.pptx_parser import extract_placeholders
from ..utils.auth import require_token

router = APIRouter(prefix="/api", tags=["parse"])


@router.post("/parse/{job_id}", response_model=ParseResponse, dependencies=[Depends(require_token)])
def parse_template(job_id: str, include_notes: bool = Query(default=False)) -> ParseResponse:
    job = job_store.maybe_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = extract_placeholders(str(job.template_path), include_notes=include_notes)
    job.placeholders = result["placeholders"]
    job.state = JobState.AWAITING_INPUT
    job.add_audit("parse", placeholder_count=len(job.placeholders), include_notes=include_notes)
    return ParseResponse(placeholders=job.placeholders)
