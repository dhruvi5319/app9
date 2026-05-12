from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.registry import job_registry
from app.models.schemas import HealthResponse, ApiErrorResponse

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    logger.info("Server started. TEMP_DIR=%s", settings.TEMP_DIR)
    yield
    # Shutdown
    logger.info("Server shutting down.")


app = FastAPI(
    title="PDF to DOCX Converter",
    description="Upload a PDF and download a DOCX.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in origins else origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Upload size limit middleware ──────────────────────────────────────────────


@app.middleware("http")
async def enforce_upload_size(request: Request, call_next):
    """Reject requests with a Content-Length header exceeding MAX_FILE_SIZE_BYTES."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_FILE_SIZE_BYTES:
        return JSONResponse(
            status_code=413,
            content=ApiErrorResponse(
                error_code="FILE_TOO_LARGE",
                message=f"Uploaded file exceeds the maximum allowed size of 50 MB.",
                detail=f"Received {content_length} bytes; limit is {settings.MAX_FILE_SIZE_BYTES} bytes.",
            ).model_dump(),
        )
    return await call_next(request)


# ── Static files ─────────────────────────────────────────────────────────────

_static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    return FileResponse(str(_static_dir / "index.html"))


# ── Health endpoint ───────────────────────────────────────────────────────────


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return server health status."""
    writable = (
        os.access(settings.TEMP_DIR, os.W_OK)
        if os.path.isdir(settings.TEMP_DIR)
        else False
    )
    return HealthResponse(
        status="ok",
        temp_dir_writable=writable,
        active_jobs=job_registry.active_count(),
    )


# Phase 3: from app.routers.convert import router as convert_router
# Phase 3: app.include_router(convert_router, prefix="/api")
# Phase 4: from app.routers.download import router as download_router
# Phase 4: app.include_router(download_router, prefix="/api")
