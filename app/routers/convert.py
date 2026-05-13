"""
app/routers/convert.py
----------------------
POST /api/convert — accepts a multipart/form-data PDF upload, validates it,
converts it to DOCX, and returns the job_id and derived filename.

HTTP response contract (from FRD F01):
  200 OK  → ConvertSuccessResponse { job_id, filename, file_size_bytes }
  400     → ApiErrorResponse { error_code: "INVALID_FILE_TYPE" }
  413     → ApiErrorResponse { error_code: "FILE_TOO_LARGE" }
  422     → ApiErrorResponse { error_code: "CONVERSION_FAILED" | "IMAGE_ONLY_PDF" }
  500     → ApiErrorResponse { error_code: "INTERNAL_ERROR" }
  503     → ApiErrorResponse { error_code: "SERVER_BUSY" }
  504     → ApiErrorResponse { error_code: "CONVERSION_TIMEOUT" }
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.registry import job_registry
from app.models.schemas import ApiErrorResponse, ConvertSuccessResponse
from app.services.conversion import (
    ConversionFailedError,
    ConversionService,
    ConversionTimeoutError,
    ImageOnlyPdfError,
)
from app.services.validation import (
    FileSizeError,
    FiletypeError,
    MimeTypeError,
    ValidationService,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level service instances (stateless — safe to reuse across requests)
_validation_service = ValidationService()
_conversion_service = ConversionService()


@router.post(
    "/convert",
    response_model=ConvertSuccessResponse,
    responses={
        400: {"model": ApiErrorResponse},
        413: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
        503: {"model": ApiErrorResponse},
        504: {"model": ApiErrorResponse},
    },
    summary="Convert PDF to DOCX",
    description=(
        "Upload a PDF file. Returns a job_id and derived filename on success. "
        "Validates magic bytes and MIME type before writing any file to disk."
    ),
    tags=["convert"],
)
async def convert_pdf(
    file: UploadFile = File(..., description="PDF file to convert"),
) -> JSONResponse:
    """Accept a PDF upload and convert it to DOCX.

    Enforces:
    - MIME type must be application/pdf
    - Magic bytes must be %PDF
    - File size must not exceed MAX_FILE_SIZE_BYTES
    - Active conversion jobs must be below MAX_CONCURRENT_JOBS
    - Conversion must complete within JOB_TIMEOUT_SECONDS
    """

    # ── 1. Concurrent job limit check ─────────────────────────────────────
    # Check BEFORE validation so we fail fast without reading the file body
    # when the server is already at capacity.
    active = job_registry.active_count()
    if active >= settings.MAX_CONCURRENT_JOBS:
        logger.warning(
            "Server busy: %d/%d active jobs", active, settings.MAX_CONCURRENT_JOBS
        )
        return JSONResponse(
            status_code=503,
            content=ApiErrorResponse(
                error_code="SERVER_BUSY",
                message=f"Server is at capacity ({active} active jobs). Please try again later.",
            ).model_dump(),
        )

    # ── 2. Validate upload ────────────────────────────────────────────────
    try:
        file_bytes = await _validation_service.validate(file)
    except MimeTypeError as exc:
        logger.info("Rejected upload '%s': MIME type invalid", file.filename)
        return JSONResponse(
            status_code=400,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )
    except FiletypeError as exc:
        logger.info("Rejected upload '%s': magic bytes invalid", file.filename)
        return JSONResponse(
            status_code=400,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )
    except FileSizeError as exc:
        logger.info(
            "Rejected upload '%s': %d bytes exceeds limit", file.filename, exc.received
        )
        return JSONResponse(
            status_code=413,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
                detail=f"Received {exc.received} bytes; limit is {exc.limit} bytes.",
            ).model_dump(),
        )

    # ── 3. Convert PDF to DOCX ────────────────────────────────────────────
    try:
        result = await _conversion_service.convert(
            file_bytes=file_bytes,
            original_filename=file.filename or "upload.pdf",
        )
    except ConversionTimeoutError as exc:
        logger.warning(
            "Conversion timeout for upload '%s'", file.filename
        )
        return JSONResponse(
            status_code=504,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )
    except ImageOnlyPdfError as exc:
        logger.info(
            "Image-only PDF rejected for upload '%s'", file.filename
        )
        return JSONResponse(
            status_code=422,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
            ).model_dump(),
        )
    except ConversionFailedError as exc:
        logger.error(
            "Conversion failed for upload '%s': %s", file.filename, exc.detail
        )
        return JSONResponse(
            status_code=422,
            content=ApiErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
                detail=exc.detail if exc.detail else None,
            ).model_dump(),
        )
    except Exception as exc:
        # Catch-all: unexpected server-side error
        logger.exception(
            "Unexpected error converting upload '%s': %s", file.filename, exc
        )
        return JSONResponse(
            status_code=500,
            content=ApiErrorResponse(
                error_code="INTERNAL_ERROR",
                message="An unexpected server error occurred. Please try again.",
            ).model_dump(),
        )

    # ── 4. Return success response ────────────────────────────────────────
    logger.info(
        "Conversion success: job_id=%s filename='%s' size=%d",
        result.job_id,
        result.derived_filename,
        result.file_size_bytes,
    )
    return JSONResponse(
        status_code=200,
        content=ConvertSuccessResponse(
            job_id=result.job_id,
            filename=result.derived_filename,
            file_size_bytes=result.file_size_bytes,
        ).model_dump(),
    )
