"""
app/services/download.py
------------------------
DownloadService — validates job state, streams the DOCX, and schedules
post-send cleanup via FastAPI BackgroundTasks.

Exceptions raised (mapped to HTTP codes by the router):
  JobNotFoundError      → 404 JOB_NOT_FOUND
  JobStillConvertingError → 202 (status: converting)
  JobFailedError        → 410 JOB_FAILED
  DownloadInternalError → 500 INTERNAL_ERROR
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.registry import job_registry
from app.models.schemas import JobState

logger = logging.getLogger(__name__)


# ── Typed Exceptions ──────────────────────────────────────────────────────────


class DownloadError(Exception):
    """Base class for all download service errors."""
    error_code: str = "DOWNLOAD_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class JobNotFoundError(DownloadError):
    """job_id not in registry (unknown, expired, or already downloaded)."""
    error_code: str = "JOB_NOT_FOUND"

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Job '{job_id}' not found, expired, or already downloaded.")


class JobStillConvertingError(DownloadError):
    """Job is still in PENDING or CONVERTING state — not ready yet."""
    error_code: str = "STILL_CONVERTING"

    def __init__(self, job_id: str) -> None:
        super().__init__(f"Job '{job_id}' is still converting.")


class JobFailedError(DownloadError):
    """Job previously failed — no DOCX to deliver."""
    error_code: str = "JOB_FAILED"

    def __init__(self, job_id: str, original_error_code: str | None = None) -> None:
        super().__init__(
            f"Job '{job_id}' failed during conversion"
            + (f" ({original_error_code})" if original_error_code else "")
            + "."
        )
        self.original_error_code = original_error_code


class DownloadInternalError(DownloadError):
    """Registry says COMPLETED but DOCX file is missing from disk."""
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, job_id: str) -> None:
        super().__init__(
            f"Job '{job_id}' is marked COMPLETED but DOCX file is missing from disk."
        )


# ── Post-download cleanup (runs as BackgroundTask) ────────────────────────────


def _post_download_cleanup(job_id: str, job_dir: Path) -> None:
    """Delete the job directory tree and mark the registry entry DOWNLOADED.

    Runs after the response has been fully sent to the client. Never raises —
    errors are logged so they do not surface as response errors.
    """
    try:
        shutil.rmtree(job_dir, ignore_errors=True)
        logger.info("Deleted temp dir for job_id=%s after download", job_id)
    except Exception as exc:
        logger.error(
            "Failed to delete temp dir for job_id=%s: %s", job_id, exc
        )
    try:
        job_registry.update(job_id, JobState.DOWNLOADED)
        logger.info("Marked job_id=%s as DOWNLOADED", job_id)
    except Exception as exc:
        logger.error(
            "Failed to update registry for job_id=%s: %s", job_id, exc
        )


# ── DownloadService ───────────────────────────────────────────────────────────


class DownloadService:
    """Validates job state, locates the DOCX on disk, and builds a FileResponse.

    Usage::

        svc = DownloadService()
        response = svc.stream_docx(job_id)
        return response

    Raises:
        JobNotFoundError          — job_id absent from registry
        JobStillConvertingError   — job is PENDING or CONVERTING
        JobFailedError            — job is in FAILED state
        DownloadInternalError     — registry COMPLETED but file missing
    """

    def stream_docx(self, job_id: str) -> FileResponse:
        """Build a streaming FileResponse for the completed DOCX.

        The FileResponse uses FastAPI's BackgroundTasks to schedule
        _post_download_cleanup once the file has been fully sent.
        """
        # ── 1. Look up job in registry ────────────────────────────────────
        record = job_registry.get(job_id)

        if record is None:
            # Unknown, expired (TTL sweep removed it), or already downloaded
            raise JobNotFoundError(job_id)

        # ── 2. State-based routing ────────────────────────────────────────
        if record.state in (JobState.PENDING, JobState.CONVERTING):
            raise JobStillConvertingError(job_id)

        if record.state == JobState.FAILED:
            raise JobFailedError(job_id, original_error_code=record.error_code)

        if record.state == JobState.DOWNLOADED:
            # Already downloaded — registry entry still present but dir is gone.
            # Treat as not found (spec: 404 JOB_NOT_FOUND).
            raise JobNotFoundError(job_id)

        # state is COMPLETED — proceed
        # ── 3. Locate DOCX on disk ────────────────────────────────────────
        job_dir = Path(settings.TEMP_DIR) / job_id
        docx_path = job_dir / f"{job_id}.docx"

        if not docx_path.is_file():
            # Registry/disk inconsistency — log and return 500
            logger.error(
                "DOCX missing for COMPLETED job_id=%s (expected %s)",
                job_id,
                docx_path,
            )
            raise DownloadInternalError(job_id)

        # ── 4. Build BackgroundTask for post-send cleanup ─────────────────
        background_tasks = BackgroundTasks()
        background_tasks.add_task(_post_download_cleanup, job_id, job_dir)

        logger.info(
            "Streaming DOCX for job_id=%s filename='%s' size=%s bytes",
            job_id,
            record.derived_filename,
            record.file_size_bytes,
        )

        # ── 5. Return FileResponse (handles Content-Length automatically) ─
        return FileResponse(
            path=str(docx_path),
            filename=record.derived_filename,
            media_type=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
            background=background_tasks,
            headers={"Cache-Control": "no-store"},
        )


# Module-level singleton
download_service = DownloadService()
