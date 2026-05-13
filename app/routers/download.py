"""
app/routers/download.py
-----------------------
Router for GET /api/download/{job_id}.

UUID v4 validation is performed in the endpoint before delegating to
DownloadService. All service exceptions are mapped to structured JSON
error responses per the API contract.

HTTP Response Map:
  200 OK              — DOCX binary stream (FileResponse)
  202 Accepted        — Job still converting
  400 Bad Request     — job_id fails UUID v4 format check
  404 Not Found       — Unknown / expired / already-downloaded job
  410 Gone            — Job previously failed
  500 Internal Error  — Registry/disk inconsistency
"""

from __future__ import annotations

import re
import logging

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.models.schemas import ApiErrorResponse
from app.services.download import (
    download_service,
    JobNotFoundError,
    JobStillConvertingError,
    JobFailedError,
    DownloadInternalError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["download"])

# UUID v4 regex — from TechArch specification
_UUID4_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
)


@router.get(
    "/download/{job_id}",
    summary="Download converted DOCX",
    response_description="Binary DOCX file stream",
    responses={
        200: {"description": "DOCX file stream"},
        202: {"description": "Job still converting"},
        400: {"description": "Invalid job_id format"},
        404: {"description": "Job not found or already downloaded"},
        410: {"description": "Job previously failed"},
        500: {"description": "Internal server error"},
    },
)
async def download_docx(job_id: str) -> FileResponse:
    """Stream the converted DOCX file for a completed conversion job.

    - Validates job_id is a UUID v4.
    - Returns 202 if the job is still converting.
    - Returns 404 if the job is unknown, expired, or already downloaded.
    - Returns 410 if the job failed.
    - Returns 200 with binary DOCX on success; post-send cleanup runs as background task.
    """
    # ── UUID v4 format validation ─────────────────────────────────────────
    if not _UUID4_RE.match(job_id):
        return JSONResponse(
            status_code=400,
            content=ApiErrorResponse(
                error_code="INVALID_JOB_ID",
                message="The provided job_id is not a valid UUID v4.",
                detail=f"job_id='{job_id}' does not match the required UUID v4 format.",
            ).model_dump(),
        )

    # ── Delegate to DownloadService ───────────────────────────────────────
    try:
        return download_service.stream_docx(job_id)

    except JobStillConvertingError:
        return JSONResponse(
            status_code=202,
            content={"status": "converting"},
        )

    except JobNotFoundError as exc:
        return JSONResponse(
            status_code=404,
            content=ApiErrorResponse(
                error_code="JOB_NOT_FOUND",
                message=exc.message,
            ).model_dump(),
        )

    except JobFailedError as exc:
        return JSONResponse(
            status_code=410,
            content=ApiErrorResponse(
                error_code="JOB_FAILED",
                message=exc.message,
                detail=exc.original_error_code,
            ).model_dump(),
        )

    except DownloadInternalError as exc:
        logger.error("Internal error during download for job_id=%s: %s", job_id, exc)
        return JSONResponse(
            status_code=500,
            content=ApiErrorResponse(
                error_code="INTERNAL_ERROR",
                message=exc.message,
            ).model_dump(),
        )

    except Exception as exc:
        logger.exception("Unexpected error during download for job_id=%s", job_id)
        return JSONResponse(
            status_code=500,
            content=ApiErrorResponse(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
                detail=str(exc),
            ).model_dump(),
        )
