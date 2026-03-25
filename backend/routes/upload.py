from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..schemas.api import UploadResponse
from ..services.job_store import job_store
from ..utils.auth import require_token
from ..utils.config import settings

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(require_token)])
async def upload_template(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are allowed")

    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb}MB limit")

    temp_path = Path(settings.temp_dir) / "incoming" / f"{uuid4()}-{file.filename}"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_bytes(content)

    job = job_store.create_job(temp_path)
    job.add_audit("upload", filename=file.filename, size=len(content))
    return UploadResponse(jobId=job.id, state=job.state.value)
