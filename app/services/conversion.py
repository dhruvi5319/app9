"""
app/services/conversion.py
--------------------------
ConversionService — converts validated PDF bytes to DOCX.

Pipeline (in order):
  1. Generate UUID v4 job_id
  2. Create isolated temp directory {TEMP_DIR}/{job_id}/ with permissions 700
  3. Write PDF bytes to {TEMP_DIR}/{job_id}/{job_id}.pdf with permissions 600
  4. Register job as CONVERTING in JobRegistry
  5. Invoke pdf2docx.Converter in a thread with JOB_TIMEOUT_SECONDS watchdog
  6. On pdf2docx failure: attempt LibreOffice headless fallback
  7. On fallback failure: clean up temp dir, raise ConversionFailedError
  8. On timeout: clean up temp dir, raise ConversionTimeoutError
  9. Detect image-only output (zero text paragraphs in DOCX)
 10. On image-only: clean up temp dir, raise ImageOnlyPdfError
 11. On success: update JobRegistry to COMPLETED, return ConversionResult

Security invariants:
  - UUID v4 used as on-disk filename, never the original filename
  - Directory permissions: 700 (owner rwx only)
  - File permissions: 600 (owner rw only)
  - No subprocess call uses shell=True
  - Temp directory deleted on ANY failure before exception propagates
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
import shutil
import stat
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from docx import Document

from app.core.config import settings
from app.core.registry import job_registry
from app.models.schemas import JobState

logger = logging.getLogger(__name__)


# ── Exception Hierarchy ───────────────────────────────────────────────────────


class ConversionError(Exception):
    """Base class for all conversion pipeline failures.

    Each subclass carries an ``error_code`` attribute that maps directly
    to the API error_code field returned to the client.
    """

    error_code: str = "CONVERSION_FAILED"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConversionTimeoutError(ConversionError):
    """Conversion exceeded JOB_TIMEOUT_SECONDS and was terminated."""

    error_code: str = "CONVERSION_TIMEOUT"

    def __init__(self) -> None:
        super().__init__(
            f"Conversion exceeded the {settings.JOB_TIMEOUT_SECONDS}-second timeout."
        )


class ConversionFailedError(ConversionError):
    """Both pdf2docx and LibreOffice fallback failed."""

    error_code: str = "CONVERSION_FAILED"

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            f"Conversion failed using both pdf2docx and LibreOffice fallback. {detail}".strip()
        )
        self.detail = detail


class ImageOnlyPdfError(ConversionError):
    """The output DOCX contains no text paragraphs — input is a scanned/image-only PDF."""

    error_code: str = "IMAGE_ONLY_PDF"

    def __init__(self) -> None:
        super().__init__(
            "The uploaded PDF contains only images and cannot be converted to editable text."
        )


# ── ConversionResult ──────────────────────────────────────────────────────────


@dataclass
class ConversionResult:
    """Returned by ConversionService.convert() on success."""

    job_id: str
    derived_filename: str   # e.g. "report.docx" derived from "report.pdf"
    file_size_bytes: int    # Size of the produced DOCX in bytes


# ── Internal pdf2docx runner (runs in thread) ─────────────────────────────────


def _run_pdf2docx(pdf_path: str, docx_path: str) -> None:
    """Invoke pdf2docx Converter. Runs inside a ThreadPoolExecutor thread.

    Must not catch exceptions — let them propagate to the future.
    """
    from pdf2docx import Converter  # import inside thread to avoid event loop issues

    cv = Converter(pdf_path)
    try:
        cv.convert(docx_path, start=0, end=None)
    finally:
        cv.close()


# ── ConversionService ─────────────────────────────────────────────────────────


class ConversionService:
    """Converts validated PDF bytes to DOCX via pdf2docx with LibreOffice fallback.

    Usage::

        svc = ConversionService()
        result = await svc.convert(file_bytes, original_filename="report.pdf")
        # result.job_id, result.derived_filename, result.file_size_bytes
    """

    async def convert(
        self,
        file_bytes: bytes,
        original_filename: str,
    ) -> ConversionResult:
        """Run the full conversion pipeline.

        Args:
            file_bytes:        Raw validated PDF bytes (from ValidationService).
            original_filename: The browser-supplied filename (used ONLY for
                               deriving the output .docx name — never used
                               as an on-disk filename).

        Returns:
            ConversionResult on success.

        Raises:
            ConversionTimeoutError:  Conversion exceeded timeout.
            ConversionFailedError:   Both converters failed.
            ImageOnlyPdfError:       Output DOCX has no text content.
        """
        # ── 1. Generate job_id and derive paths ───────────────────────────
        job_id = str(uuid.uuid4())

        # Derive output filename from original (stem only, force .docx extension)
        original_stem = Path(original_filename).stem or job_id
        derived_filename = f"{original_stem}.docx"

        job_dir = Path(settings.TEMP_DIR) / job_id
        pdf_path = job_dir / f"{job_id}.pdf"
        docx_path = job_dir / f"{job_id}.docx"

        # ── 2. Create isolated temp directory (permissions: 700) ──────────
        job_dir.mkdir(parents=True, exist_ok=False)
        os.chmod(job_dir, stat.S_IRWXU)  # 700: owner rwx only

        # ── 3. Write PDF bytes (permissions: 600) ─────────────────────────
        pdf_path.write_bytes(file_bytes)
        os.chmod(pdf_path, stat.S_IRUSR | stat.S_IWUSR)  # 600: owner rw only

        # ── 4. Register job as CONVERTING ─────────────────────────────────
        job_registry.register(
            job_id=job_id,
            original_filename=original_filename,
            derived_filename=derived_filename,
        )
        job_registry.update(
            job_id=job_id,
            state=JobState.CONVERTING,
            file_size_bytes=len(file_bytes),
        )

        logger.info(
            "Starting conversion job_id=%s original='%s' size=%d bytes",
            job_id,
            original_filename,
            len(file_bytes),
        )

        # ── 5. Attempt pdf2docx conversion (with timeout watchdog) ────────
        pdf2docx_succeeded = False
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    _run_pdf2docx,
                    str(pdf_path),
                    str(docx_path),
                )
                try:
                    future.result(timeout=settings.JOB_TIMEOUT_SECONDS)
                    pdf2docx_succeeded = True
                    logger.info("pdf2docx succeeded for job_id=%s", job_id)
                except concurrent.futures.TimeoutError:
                    logger.warning("pdf2docx timed out for job_id=%s", job_id)
                    self._cleanup(job_id, job_dir)
                    job_registry.update(
                        job_id=job_id,
                        state=JobState.FAILED,
                        error_code="CONVERSION_TIMEOUT",
                    )
                    raise ConversionTimeoutError()
                except Exception as exc:
                    logger.warning(
                        "pdf2docx failed for job_id=%s: %s", job_id, exc
                    )
                    # Fall through to LibreOffice fallback

        except ConversionTimeoutError:
            raise  # Re-raise after cleanup (already done above)

        # ── 6. LibreOffice fallback (only if pdf2docx failed) ────────────
        if not pdf2docx_succeeded:
            logger.info(
                "Attempting LibreOffice fallback for job_id=%s", job_id
            )
            try:
                subprocess.run(
                    [
                        "libreoffice",
                        "--headless",
                        "--convert-to",
                        "docx",
                        str(pdf_path),
                        "--outdir",
                        str(job_dir),
                    ],
                    timeout=settings.JOB_TIMEOUT_SECONDS,
                    check=True,
                    shell=False,   # SECURITY: never use shell=True
                    capture_output=True,
                )
                # LibreOffice names the output {stem}.docx in job_dir
                # The stem of our PDF is job_id (e.g. "abc-123.pdf" → "abc-123.docx")
                lo_output = job_dir / f"{job_id}.docx"
                if not lo_output.exists():
                    raise FileNotFoundError(
                        f"LibreOffice did not produce expected output: {lo_output}"
                    )
                docx_path = lo_output
                logger.info("LibreOffice fallback succeeded for job_id=%s", job_id)

            except subprocess.TimeoutExpired:
                logger.warning(
                    "LibreOffice fallback timed out for job_id=%s", job_id
                )
                self._cleanup(job_id, job_dir)
                job_registry.update(
                    job_id=job_id,
                    state=JobState.FAILED,
                    error_code="CONVERSION_TIMEOUT",
                )
                raise ConversionTimeoutError()

            except Exception as exc:
                logger.error(
                    "LibreOffice fallback failed for job_id=%s: %s", job_id, exc
                )
                self._cleanup(job_id, job_dir)
                job_registry.update(
                    job_id=job_id,
                    state=JobState.FAILED,
                    error_code="CONVERSION_FAILED",
                )
                raise ConversionFailedError(detail=str(exc))

        # ── 7. Verify DOCX was produced ───────────────────────────────────
        if not docx_path.exists():
            self._cleanup(job_id, job_dir)
            job_registry.update(
                job_id=job_id,
                state=JobState.FAILED,
                error_code="CONVERSION_FAILED",
            )
            raise ConversionFailedError(detail="Output DOCX file not found after conversion.")

        # ── 8. Image-only detection ────────────────────────────────────────
        try:
            doc = Document(str(docx_path))
            has_text = any(
                para.text.strip()
                for para in doc.paragraphs
            )
        except Exception as exc:
            logger.error(
                "Failed to inspect DOCX for job_id=%s: %s", job_id, exc
            )
            self._cleanup(job_id, job_dir)
            job_registry.update(
                job_id=job_id,
                state=JobState.FAILED,
                error_code="CONVERSION_FAILED",
            )
            raise ConversionFailedError(detail=f"Could not inspect output DOCX: {exc}")

        if not has_text:
            logger.warning(
                "Image-only PDF detected for job_id=%s — no text paragraphs in output",
                job_id,
            )
            self._cleanup(job_id, job_dir)
            job_registry.update(
                job_id=job_id,
                state=JobState.FAILED,
                error_code="IMAGE_ONLY_PDF",
            )
            raise ImageOnlyPdfError()

        # ── 9. Success: measure DOCX size, update registry ─────────────────
        docx_size = docx_path.stat().st_size
        job_registry.update(
            job_id=job_id,
            state=JobState.COMPLETED,
            file_size_bytes=docx_size,
        )

        logger.info(
            "Conversion complete: job_id=%s derived='%s' docx_size=%d bytes",
            job_id,
            derived_filename,
            docx_size,
        )

        return ConversionResult(
            job_id=job_id,
            derived_filename=derived_filename,
            file_size_bytes=docx_size,
        )

    # ── Private helpers ───────────────────────────────────────────────────

    def _cleanup(self, job_id: str, job_dir: Path) -> None:
        """Delete the job's temp directory tree. Called on any failure.

        Never raises — cleanup failures are logged and swallowed so they
        don't mask the original exception.
        """
        try:
            if job_dir.exists():
                shutil.rmtree(job_dir)
                logger.info("Cleaned up temp dir for job_id=%s", job_id)
        except Exception as exc:
            logger.error(
                "Failed to clean up temp dir for job_id=%s: %s", job_id, exc
            )
