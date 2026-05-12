from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


# ── Job State Enum ────────────────────────────────────────────────────────────


class JobState(str, Enum):
    PENDING = "PENDING"
    CONVERTING = "CONVERTING"
    COMPLETED = "COMPLETED"
    DOWNLOADED = "DOWNLOADED"
    FAILED = "FAILED"


# ── Job Record (in-memory registry entry) ────────────────────────────────────


@dataclass
class JobRecord:
    job_id: str
    state: JobState
    original_filename: str
    derived_filename: str
    file_size_bytes: Optional[int]
    created_at: datetime
    updated_at: datetime
    error_code: Optional[str]


# ── API Response Models ───────────────────────────────────────────────────────


class ConvertSuccessResponse(BaseModel):
    job_id: str
    filename: str
    file_size_bytes: int


class ApiErrorResponse(BaseModel):
    error_code: str
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    temp_dir_writable: bool
    active_jobs: int
