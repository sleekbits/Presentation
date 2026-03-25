from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from ..models.job import Job
from ..utils.config import settings


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create_job(self, template_path: Path) -> Job:
        with self._lock:
            job_id = str(uuid4())
            job = Job(
                id=job_id,
                template_path=template_path,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.file_ttl_minutes),
            )
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> Job:
        return self._jobs[job_id]

    def maybe_get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [jid for jid, job in self._jobs.items() if job.expires_at <= now]
        for jid in expired:
            job = self._jobs.pop(jid)
            if job.template_path.exists():
                job.template_path.unlink(missing_ok=True)
            if job.output_path and job.output_path.exists():
                job.output_path.unlink(missing_ok=True)
            job_dir = settings.temp_dir / jid
            if job_dir.exists():
                shutil.rmtree(job_dir, ignore_errors=True)


job_store = JobStore()
