import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from app.models.schemas import JobRecord, JobState


class JobRegistry:
    def __init__(self) -> None:
        self._store: Dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def register(
        self,
        job_id: str,
        original_filename: str,
        derived_filename: str,
    ) -> JobRecord:
        """Register a new job in PENDING state."""
        now = datetime.now(timezone.utc)
        record = JobRecord(
            job_id=job_id,
            state=JobState.PENDING,
            original_filename=original_filename,
            derived_filename=derived_filename,
            file_size_bytes=None,
            created_at=now,
            updated_at=now,
            error_code=None,
        )
        with self._lock:
            self._store[job_id] = record
        return record

    def update(
        self,
        job_id: str,
        state: JobState,
        file_size_bytes: Optional[int] = None,
        error_code: Optional[str] = None,
    ) -> Optional[JobRecord]:
        """Update job state. Returns updated record or None if not found."""
        with self._lock:
            record = self._store.get(job_id)
            if record is None:
                return None
            record.state = state
            record.updated_at = datetime.now(timezone.utc)
            if file_size_bytes is not None:
                record.file_size_bytes = file_size_bytes
            if error_code is not None:
                record.error_code = error_code
            return record

    def get(self, job_id: str) -> Optional[JobRecord]:
        """Retrieve a job record by ID."""
        with self._lock:
            return self._store.get(job_id)

    def delete(self, job_id: str) -> bool:
        """Remove a job record. Returns True if it existed."""
        with self._lock:
            return self._store.pop(job_id, None) is not None

    def active_count(self) -> int:
        """Count jobs in CONVERTING state."""
        with self._lock:
            return sum(
                1 for r in self._store.values() if r.state == JobState.CONVERTING
            )

    def all_records(self) -> list[JobRecord]:
        """Return a snapshot of all records (for TTL sweep)."""
        with self._lock:
            return list(self._store.values())


# Module-level singleton — imported across the application
job_registry = JobRegistry()
