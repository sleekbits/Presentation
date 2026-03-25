from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class JobState(str, Enum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    AWAITING_INPUT = "awaiting_input"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AuditEvent:
    event: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Job:
    id: str
    template_path: Path
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    state: JobState = JobState.UPLOADED
    placeholders: list[dict[str, Any]] = field(default_factory=list)
    field_config: dict[str, Any] = field(default_factory=dict)
    output_path: Path | None = None
    error: str | None = None
    audit_log: list[AuditEvent] = field(default_factory=list)

    def add_audit(self, event: str, **metadata: Any) -> None:
        self.audit_log.append(AuditEvent(event=event, metadata=metadata))
