"""
app/services/validation.py
--------------------------
ValidationService — validates an incoming UploadFile before any disk I/O.

Checks performed (in order):
  1. MIME type check: Content-Type header must be application/pdf
  2. Magic byte check: first 4 bytes of file body must be %PDF (0x25 0x50 0x44 0x46)
  3. Size check: total byte count must not exceed settings.MAX_FILE_SIZE_BYTES

Raises a typed ValidationError subclass on the first failure encountered.
Returns the complete file bytes on success.
"""

from __future__ import annotations

import logging

from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Exception Hierarchy ───────────────────────────────────────────────────────


class ValidationError(Exception):
    """Base class for all upload validation failures.

    Each subclass carries an ``error_code`` attribute that maps directly
    to the API error_code field returned to the client.
    """

    error_code: str = "VALIDATION_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MimeTypeError(ValidationError):
    """Content-Type header is not application/pdf."""

    error_code: str = "INVALID_FILE_TYPE"

    def __init__(self) -> None:
        super().__init__(
            "Uploaded file Content-Type is not application/pdf."
        )


class FiletypeError(ValidationError):
    """File body does not begin with the PDF magic bytes (%PDF)."""

    error_code: str = "INVALID_FILE_TYPE"

    def __init__(self) -> None:
        super().__init__(
            "Uploaded file does not have a valid PDF signature (magic bytes %PDF)."
        )


class FileSizeError(ValidationError):
    """File byte count exceeds MAX_FILE_SIZE_BYTES."""

    error_code: str = "FILE_TOO_LARGE"

    def __init__(self, received: int, limit: int) -> None:
        super().__init__(
            f"File size {received} bytes exceeds the {limit}-byte limit."
        )
        self.received = received
        self.limit = limit


# ── PDF magic bytes constant ──────────────────────────────────────────────────

_PDF_MAGIC = b"%PDF"  # First 4 bytes of every valid PDF file


# ── ValidationService ─────────────────────────────────────────────────────────


class ValidationService:
    """Validates an uploaded file before any disk I/O.

    Usage::

        svc = ValidationService()
        file_bytes = await svc.validate(upload_file)
        # file_bytes is the complete content ready for disk write
    """

    async def validate(self, file: UploadFile) -> bytes:
        """Validate *file* and return its bytes if all checks pass.

        Raises:
            MimeTypeError:  Content-Type header is not application/pdf.
            FiletypeError:  First 4 bytes are not %PDF.
            FileSizeError:  Byte count exceeds MAX_FILE_SIZE_BYTES.
        """
        # ── 1. MIME type check ─────────────────────────────────────────────
        # FastAPI exposes the browser-supplied Content-Type for the file part.
        # We treat absence of the header as a failure (same as wrong type).
        content_type = file.content_type or ""
        # Strip parameters such as "; charset=utf-8" before comparing.
        mime = content_type.split(";")[0].strip().lower()
        if mime != "application/pdf":
            logger.warning(
                "MIME type check failed: received '%s'", content_type
            )
            raise MimeTypeError()

        # ── 2. Read full file bytes ────────────────────────────────────────
        # Read all bytes so we can check both magic bytes and total size
        # without seeking (SpooledTemporaryFile may not be seekable).
        raw: bytes = await file.read()

        # ── 3. Magic byte check ────────────────────────────────────────────
        # Must happen BEFORE size check and BEFORE any disk write.
        # A zero-length file will also fail this check correctly.
        if not raw[:4] == _PDF_MAGIC:
            logger.warning(
                "Magic byte check failed for file '%s': got %r",
                file.filename,
                raw[:8],
            )
            raise FiletypeError()

        # ── 4. Size check ──────────────────────────────────────────────────
        # The middleware in main.py already rejects requests whose
        # Content-Length header exceeds the limit, but the header can be
        # absent or spoofed.  Count actual bytes as a second enforcement.
        total = len(raw)
        if total > settings.MAX_FILE_SIZE_BYTES:
            logger.warning(
                "Size check failed for file '%s': %d bytes (limit %d)",
                file.filename,
                total,
                settings.MAX_FILE_SIZE_BYTES,
            )
            raise FileSizeError(received=total, limit=settings.MAX_FILE_SIZE_BYTES)

        logger.debug(
            "Validation passed for file '%s': %d bytes", file.filename, total
        )
        return raw
