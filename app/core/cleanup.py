"""
app/core/cleanup.py
-------------------
CleanupService — TTL-based background sweep for orphaned temp files.

Runs on a periodic asyncio task (started in main.py lifespan). Every
SWEEP_INTERVAL_MINUTES it scans TEMP_DIR and deletes any job subdirectory
older than TTL_MINUTES. Corresponding JobRegistry entries are removed.

Logs: count of directories deleted and bytes freed (no file content logged).
"""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path

from app.core.config import settings
from app.core.registry import job_registry

logger = logging.getLogger(__name__)


class CleanupService:
    """Scans TEMP_DIR and removes expired job directories.

    Usage (called by the periodic asyncio task in main.py)::

        svc = CleanupService()
        result = await svc.sweep()
        # result = {"deleted": N, "freed_bytes": M}
    """

    async def sweep(self) -> dict:
        """Delete all job directories older than TTL_MINUTES.

        Returns a dict with ``deleted`` (count) and ``freed_bytes`` (int).
        Never raises — errors per directory are logged and skipped.
        """
        temp_dir = Path(settings.TEMP_DIR)
        if not temp_dir.is_dir():
            logger.warning("TEMP_DIR %s does not exist — skipping sweep", temp_dir)
            return {"deleted": 0, "freed_bytes": 0}

        now = time.time()
        ttl_seconds = settings.TTL_MINUTES * 60
        deleted_count = 0
        freed_bytes = 0

        try:
            entries = list(temp_dir.iterdir())
        except Exception as exc:
            logger.error("Failed to list TEMP_DIR for sweep: %s", exc)
            return {"deleted": 0, "freed_bytes": 0}

        for entry in entries:
            if not entry.is_dir():
                continue

            try:
                # Use mtime as the age proxy — set when directory is created
                # and not updated during normal operation.
                age_seconds = now - entry.stat().st_mtime
            except Exception as exc:
                logger.warning("Cannot stat directory %s: %s", entry, exc)
                continue

            if age_seconds <= ttl_seconds:
                continue

            # Directory is expired — measure size before deletion
            dir_bytes = 0
            try:
                dir_bytes = sum(
                    f.stat().st_size
                    for f in entry.rglob("*")
                    if f.is_file()
                )
            except Exception:
                pass  # Best-effort size measurement

            try:
                shutil.rmtree(entry, ignore_errors=True)
                deleted_count += 1
                freed_bytes += dir_bytes
                # Remove registry entry if present (entry.name is the job_id)
                job_registry.delete(entry.name)
                logger.info(
                    "TTL sweep: deleted job_dir=%s age=%.0fs freed=%d bytes",
                    entry.name,
                    age_seconds,
                    dir_bytes,
                )
            except Exception as exc:
                logger.error(
                    "TTL sweep: failed to delete %s: %s", entry, exc
                )

        logger.info(
            "TTL sweep complete: deleted=%d dirs, freed=%d bytes",
            deleted_count,
            freed_bytes,
        )
        return {"deleted": deleted_count, "freed_bytes": freed_bytes}


# Module-level singleton — imported by main.py lifespan
cleanup_service = CleanupService()
