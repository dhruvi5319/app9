# Technical Architecture Document
# PDF to DOCX Converter (PDFConverter)

**Version:** 1.0
**Date:** 2026-05-12
**Status:** Draft
**Based on:** PRD-PDFConverter.md v1.0 · FRD-PDFConverter.md v1.0

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Model & Storage Schema](#3-data-model--storage-schema)
4. [API Design](#4-api-design)
5. [Security Architecture](#5-security-architecture)
6. [Technology Stack](#6-technology-stack)
7. [Integration Points](#7-integration-points)

---

## 1. Architectural Overview

### 1.1 Pattern

PDFConverter uses a **Thin-Server Synchronous Request/Response** architecture. There is no persistent database, no message queue, and no asynchronous job worker for v1. The entire conversion lifecycle — receive upload → validate → convert → stream download → delete temp files — is handled within a single HTTP request pair (`POST /api/convert` + `GET /api/download/{job_id}`). An in-process job registry (Python dict with thread-safe access) tracks active job state. A periodic background sweep handles orphaned temp files.

This pattern is chosen deliberately: the system's scope is minimal, the conversion time is bounded (60-second timeout), and eliminating a queue/worker tier reduces operational complexity with no functional loss for a single-purpose tool.

### 1.2 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                          User's Browser                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Vanilla JS SPA (index.html + app.js + styles.css)            │  │
│  │                                                                │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Upload UI  │  │ State Machine│  │  Status / Error Banner │ │  │
│  │  │ (F00)      │  │ IDLE→SUCCESS │  │  (F03)                 │ │  │
│  │  └────────────┘  └──────────────┘  └────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────┘  │
│               │  POST /api/convert (multipart)                       │
│               │  GET  /api/download/{job_id}                         │
└───────────────┼──────────────────────────────────────────────────────┘
                │  HTTPS
┌───────────────▼──────────────────────────────────────────────────────┐
│                     Python / FastAPI Server                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  API Layer  (routers/convert.py · routers/download.py)       │    │
│  │                                                              │    │
│  │  POST /api/convert            GET /api/download/{job_id}     │    │
│  └──────────────────┬───────────────────────┬───────────────────┘    │
│                     │                       │                        │
│  ┌──────────────────▼───────────┐  ┌────────▼────────────────────┐   │
│  │  Validation Service          │  │  Download Service           │   │
│  │  (services/validation.py)    │  │  (services/download.py)     │   │
│  │  • Magic byte check          │  │  • UUID format check        │   │
│  │  • Size enforcement          │  │  • Job registry lookup      │   │
│  │  • MIME header check         │  │  • Streaming file delivery  │   │
│  └──────────────────┬───────────┘  │  • Post-download cleanup    │   │
│                     │              └─────────────────────────────┘   │
│  ┌──────────────────▼───────────┐                                    │
│  │  Conversion Service          │  ┌─────────────────────────────┐   │
│  │  (services/conversion.py)    │  │  Job Registry               │   │
│  │  • Write PDF to temp dir     │  │  (core/registry.py)         │   │
│  │  • pdf2docx (primary)        │◄─►  In-memory dict (thread-safe)│  │
│  │  • LibreOffice (fallback)    │  │  Tracks: PENDING/CONVERTING  │   │
│  │  • 60s timeout watchdog      │  │         /COMPLETED/FAILED    │   │
│  │  • Image-only PDF detection  │  └─────────────────────────────┘   │
│  │  • Temp file cleanup         │                                    │
│  └──────────────────────────────┘  ┌─────────────────────────────┐   │
│                                    │  TTL Sweep                  │   │
│  ┌─────────────────────────────┐   │  (core/cleanup.py)          │   │
│  │  Temp File System           │   │  Runs every 10 min          │   │
│  │  /tmp/pdfconverter/         │   │  Deletes dirs > 60 min old  │   │
│  │    {job_id}/                │◄──│                             │   │
│  │      {job_id}.pdf           │   └─────────────────────────────┘   │
│  │      {job_id}.docx          │                                    │
│  └─────────────────────────────┘                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.3 Deployment Topology

```
┌──────────────────────────────────────────────────────┐
│  Cloud PaaS (Render / Railway / Fly.io)  OR  VPS     │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  Container / Process                         │    │
│  │  • Python 3.11+                              │    │
│  │  • FastAPI + Uvicorn (ASGI)                 │    │
│  │  • pdf2docx + python-docx                   │    │
│  │  • LibreOffice headless (optional fallback) │    │
│  │  • Static files served by FastAPI or Nginx  │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  Ephemeral Filesystem                        │    │
│  │  /tmp/pdfconverter/   (temp jobs)            │    │
│  │  /app/static/         (frontend assets)      │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  No external DB · No Redis · No object storage      │
└──────────────────────────────────────────────────────┘
         │
         │  HTTPS (TLS terminated at edge / load balancer)
         ▼
   User's Browser
```

### 1.4 Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask | Native async support, automatic OpenAPI docs, built-in request validation via Pydantic, better performance for streaming |
| Synchronous conversion (no queue) | Job timeout is bounded at 60s; queue adds operational overhead not justified by v1 load |
| In-memory job registry (dict) | No external dependencies; sufficient for single-process deployment; upgrade path to Redis if scaling required |
| No persistent database | No user data to store; temp file TTL handles cleanup; keeps deployment simple |
| UUID v4 job IDs as on-disk filenames | Prevents path traversal; provides sufficient entropy against guessing |
| Streaming file delivery | Avoids loading entire DOCX into server RAM; correct for potentially large output files |
| Single-process background sweep | `asyncio` periodic task or `APScheduler` job; no external scheduler needed |

---

## 2. Component Architecture

### 2.1 Backend Components

```
app/
├── main.py                  # FastAPI app factory, middleware, startup/shutdown hooks
├── routers/
│   ├── convert.py           # POST /api/convert endpoint
│   └── download.py          # GET /api/download/{job_id} endpoint
├── services/
│   ├── validation.py        # File type, size, magic byte validation logic
│   ├── conversion.py        # pdf2docx + LibreOffice orchestration, timeout watchdog
│   └── download.py          # Job lookup, streaming response builder, post-download cleanup
├── core/
│   ├── config.py            # Environment variable loading (TEMP_DIR, MAX_FILE_SIZE_BYTES, etc.)
│   ├── registry.py          # Thread-safe in-memory job state registry
│   └── cleanup.py           # TTL background sweep task
├── models/
│   └── schemas.py           # Pydantic request/response models + TypeScript-mirrored interfaces
└── static/                  # Served directly by FastAPI or upstream Nginx
    ├── index.html
    ├── app.js
    └── styles.css
```

#### `main.py` — Application Entry Point

Responsibilities:
- Create and configure the FastAPI application instance
- Register routers (`/api/convert`, `/api/download`)
- Mount `/static` directory for frontend assets
- Register startup event: initialise job registry, start TTL sweep background task
- Register shutdown event: cancel background task gracefully
- Configure CORS (allow same-origin or configured origins)
- Configure upload size limits (enforce `MAX_FILE_SIZE_BYTES` at middleware level)

#### `routers/convert.py` — Upload & Conversion Router

Responsibilities:
- Accept `POST /api/convert` with `multipart/form-data`
- Delegate to `ValidationService` for magic byte + size checks
- Check concurrent job limit via `JobRegistry`
- Delegate to `ConversionService` for the conversion pipeline
- Return structured JSON success or error response

#### `routers/download.py` — Download Router

Responsibilities:
- Accept `GET /api/download/{job_id}`
- Validate `job_id` format (UUID v4 regex)
- Delegate to `DownloadService` for job lookup and file streaming
- Return `StreamingResponse` on success or JSON error on failure

#### `services/validation.py` — Validation Service

Responsibilities:
- Read first 8 bytes from upload stream and check `%PDF` magic bytes
- Check `Content-Length` header if present
- Count actual bytes received; reject if `> MAX_FILE_SIZE_BYTES`
- Return validated file bytes or raise typed validation exception

#### `services/conversion.py` — Conversion Service

Responsibilities:
- Generate UUID v4 `job_id`
- Create `{TEMP_DIR}/{job_id}/` directory with permissions `700`
- Write validated bytes to `{TEMP_DIR}/{job_id}/{job_id}.pdf` with permissions `600`
- Register job as `CONVERTING` in `JobRegistry`
- Invoke `pdf2docx.parse()` in a thread with `JOB_TIMEOUT_SECONDS` watchdog
- On timeout: kill thread (best effort), delete temp dir, raise `ConversionTimeoutError`
- On `pdf2docx` exception: attempt LibreOffice headless fallback via `subprocess.run`
- On fallback failure: delete temp dir, raise `ConversionFailedError`
- Detect image-only output (zero text paragraphs in DOCX); raise `ImageOnlyPdfError`
- On success: update `JobRegistry` to `COMPLETED`, return `job_id` + derived filename

#### `services/download.py` — Download Service

Responsibilities:
- Look up `job_id` in `JobRegistry`; raise `JobNotFoundError` / `JobFailedError` as appropriate
- Locate `{TEMP_DIR}/{job_id}/{job_id}.docx` on disk
- Build `StreamingResponse` with correct `Content-Type`, `Content-Disposition`, `Content-Length` headers
- Register a post-send callback to delete `{TEMP_DIR}/{job_id}/` and update registry to `DOWNLOADED`

#### `core/config.py` — Configuration

Responsibilities:
- Load all environment variables with typed defaults using `pydantic-settings`
- Expose a single `Settings` singleton imported across the application

#### `core/registry.py` — Job Registry

Responsibilities:
- Maintain a `dict[str, JobState]` protected by `threading.Lock` (or `asyncio.Lock` for async paths)
- Expose `register(job_id)`, `update(job_id, state)`, `get(job_id)`, `delete(job_id)` methods
- Store per-job: `job_id`, `state`, `original_filename`, `derived_filename`, `file_size_bytes`, `created_at`

#### `core/cleanup.py` — TTL Background Sweep

Responsibilities:
- Run on `asyncio` periodic task every `SWEEP_INTERVAL_MINUTES`
- Scan all subdirectories of `TEMP_DIR`
- For each, read creation timestamp from directory `stat` or `created_at` marker file
- Delete subdirectory if `age > TTL_MINUTES`
- Remove corresponding `JobRegistry` entry if present
- Log sweep results (count deleted, bytes freed — no file content)

---

### 2.2 Frontend Components

```
static/
├── index.html      # Single HTML page; semantic markup, ARIA attributes
├── app.js          # All UI logic; no framework dependencies
└── styles.css      # Minimal stylesheet; responsive layout
```

#### `index.html` — Single Page

Structure:
- Drop zone `<div>` containing `<input type="file" accept=".pdf,application/pdf">`
- Filename + size display area
- "Convert to DOCX" `<button>`
- `<progress>` element (upload progress bar)
- Status banner `<div>` with `aria-live="polite"` for screen reader announcements
- Error detail `<p>` (hidden unless in `ERROR` state)
- "Try Again" `<button>` (visible in `ERROR` state)
- "Convert Another File" `<a>` (visible in `SUCCESS` state)

#### `app.js` — Application Logic

State machine implementation:

```
States: IDLE → UPLOADING → CONVERTING → SUCCESS
                                      ↘ ERROR → IDLE (Try Again)
```

Responsibilities:
- Manage UI state transitions (`setState(newState)`)
- Handle file picker `change` event and drag-and-drop `drop` event
- Client-side type validation (`file.type`, `file.name` extension)
- Client-side size validation (`file.size`)
- `POST /api/convert` via `XMLHttpRequest` (for upload progress events)
- Update `<progress>` element from `xhr.upload.onprogress`
- On success: issue `GET /api/download/{job_id}` via `<a download>` anchor click or `fetch`
- Map server error codes to user-facing messages (Error Message Map)
- "Try Again" handler: reset state to `IDLE`, clear file input
- Keyboard accessibility: `Enter`/`Space` on drop zone, `Tab` focus order

---

## 3. Data Model & Storage Schema

PDFConverter has **no relational database**. All state is ephemeral: the filesystem holds transient files; an in-memory Python dict holds job metadata during the request lifecycle. This section documents both.

### 3.1 Temp File System Layout

```
/tmp/pdfconverter/                    ← TEMP_DIR (configurable)
├── {job_id_1}/                       ← dir permissions: 700
│   ├── {job_id_1}.pdf                ← file permissions: 600
│   └── {job_id_1}.docx               ← file permissions: 600
├── {job_id_2}/
│   ├── {job_id_2}.pdf
│   └── {job_id_2}.docx
└── ...
```

**Naming convention:** All on-disk names use the UUID v4 `job_id`. The original filename is never written to the filesystem.

**Lifecycle:**
- `.pdf` written on upload acceptance
- `.docx` written on conversion success
- Both deleted immediately after download delivery
- Both deleted immediately on conversion failure
- TTL sweep deletes the entire `{job_id}/` directory if it is older than `TTL_MINUTES`

---

### 3.2 In-Memory Job Registry Schema

The job registry is a Python dict: `Dict[str, JobRecord]`. It is the only "database" in the system.

**`JobRecord` data class:**

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class JobState(str, Enum):
    PENDING    = "PENDING"     # Job accepted, not yet converting
    CONVERTING = "CONVERTING"  # Conversion in progress
    COMPLETED  = "COMPLETED"   # Conversion succeeded; files on disk pending download
    DOWNLOADED = "DOWNLOADED"  # Download delivered; files deleted
    FAILED     = "FAILED"      # Conversion failed; files deleted

@dataclass
class JobRecord:
    job_id:           str             # UUID v4
    state:            JobState        # Current job state
    original_filename: str            # Original PDF filename from Content-Disposition
    derived_filename: str             # Output DOCX filename (*.pdf → *.docx)
    file_size_bytes:  Optional[int]   # Size of output DOCX in bytes (set after conversion)
    created_at:       datetime        # UTC timestamp of job creation
    updated_at:       datetime        # UTC timestamp of last state change
    error_code:       Optional[str]   # Error code if state == FAILED
```

**State Transitions:**

```
                 ┌──────────────┐
  job accepted   │   PENDING    │
 ───────────────►│              │
                 └──────┬───────┘
                        │ conversion starts
                        ▼
                 ┌──────────────┐
                 │  CONVERTING  │
                 └──────┬───────┘
              ┌─────────┴──────────┐
      success │                    │ failure / timeout
              ▼                    ▼
       ┌────────────┐       ┌──────────┐
       │  COMPLETED │       │  FAILED  │
       └──────┬─────┘       └──────────┘
              │ download delivered
              ▼
       ┌────────────┐
       │ DOWNLOADED │
       └────────────┘
```

---

### 3.3 Configuration Schema (Environment Variables)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TEMP_DIR` | `str` | `/tmp/pdfconverter` | Root directory for all job temp files |
| `MAX_FILE_SIZE_BYTES` | `int` | `52428800` | Hard upload size cap (50 MB) |
| `JOB_TIMEOUT_SECONDS` | `int` | `60` | Per-job conversion timeout |
| `MAX_CONCURRENT_JOBS` | `int` | `5` | Max simultaneous active conversions |
| `TTL_MINUTES` | `int` | `60` | Orphaned file TTL before sweep deletes |
| `SWEEP_INTERVAL_MINUTES` | `int` | `10` | Frequency of TTL sweep |
| `ALLOWED_ORIGINS` | `str` | `*` | CORS allowed origins (comma-separated) |
| `LOG_LEVEL` | `str` | `INFO` | Application log level |

---

## 4. API Design

### 4.1 API Summary

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/convert` | Upload a PDF; trigger conversion; return `job_id` |
| `GET` | `/api/download/{job_id}` | Download the converted DOCX file |
| `GET` | `/api/health` | Health check endpoint |

All API responses use `application/json` except the successful `GET /api/download/{job_id}` response (binary DOCX stream).

---

### 4.2 TypeScript Interfaces

These interfaces define the shape of all JSON payloads exchanged between the frontend and backend.

```typescript
// ── Job States ──────────────────────────────────────────────────────────────

type JobState = "PENDING" | "CONVERTING" | "COMPLETED" | "DOWNLOADED" | "FAILED";

// ── POST /api/convert ────────────────────────────────────────────────────────

/**
 * Request: multipart/form-data
 * Field name: "file"
 * Constraints: PDF only, ≤ 50 MB
 */
interface ConvertRequest {
  file: File; // Browser File object; transmitted as multipart field
}

/**
 * Response: 200 OK — conversion succeeded
 */
interface ConvertSuccessResponse {
  job_id: string;           // UUID v4
  filename: string;         // Derived DOCX filename (e.g. "report.docx")
  file_size_bytes: number;  // Size of output DOCX in bytes
}

// ── GET /api/download/{job_id} ───────────────────────────────────────────────

/**
 * Path parameter
 */
interface DownloadPathParams {
  job_id: string; // UUID v4 — pattern: [0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}
}

/**
 * Response: 200 OK — binary DOCX stream
 * Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
 * Content-Disposition: attachment; filename="{derived_filename}"
 * Content-Length: {file_size_bytes}
 */
type DownloadSuccessResponse = ArrayBuffer; // Raw DOCX bytes

/**
 * Response: 202 Accepted — job still converting (client should retry)
 */
interface DownloadConvertingResponse {
  status: "converting";
}

// ── Error Response (all error cases) ────────────────────────────────────────

interface ApiErrorResponse {
  error_code: ErrorCode;    // Machine-readable error code
  message: string;          // Developer-facing message (not shown to users)
  detail?: string;          // Optional additional context
}

// ── Error Codes ──────────────────────────────────────────────────────────────

type ErrorCode =
  | "INVALID_FILE_TYPE"   // 400 — Not a valid PDF by magic bytes or MIME
  | "FILE_TOO_LARGE"      // 413 — Exceeds MAX_FILE_SIZE_BYTES
  | "CONVERSION_TIMEOUT"  // 504 — Job killed after JOB_TIMEOUT_SECONDS
  | "CONVERSION_FAILED"   // 422 — Both pdf2docx and LibreOffice failed
  | "IMAGE_ONLY_PDF"      // 422 — Output DOCX has no text content
  | "SERVER_BUSY"         // 503 — Concurrent job limit reached
  | "INTERNAL_ERROR"      // 500 — Unexpected server-side exception
  | "JOB_NOT_FOUND"       // 404 — No job with this ID (unknown / expired / already downloaded)
  | "JOB_FAILED"          // 410 — Job previously failed
  | "INVALID_JOB_ID";     // 400 — job_id fails UUID v4 regex validation

// ── GET /api/health ──────────────────────────────────────────────────────────

interface HealthResponse {
  status: "ok";
  temp_dir_writable: boolean;
  active_jobs: number;
}
```

---

### 4.3 Endpoint Specifications

#### `POST /api/convert`

**Request:**

| Property | Value |
|----------|-------|
| Method | `POST` |
| Path | `/api/convert` |
| Content-Type | `multipart/form-data` |
| Auth | None |

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `file` | Binary (file) | Yes | MIME `application/pdf`; magic bytes `%PDF`; ≤ 52,428,800 bytes |

**Responses:**

| Status | Condition | Body |
|--------|-----------|------|
| `200 OK` | Conversion successful | `ConvertSuccessResponse` |
| `400 Bad Request` | Invalid file type (magic bytes or MIME) | `ApiErrorResponse { error_code: "INVALID_FILE_TYPE" }` |
| `413 Request Entity Too Large` | File exceeds 50 MB | `ApiErrorResponse { error_code: "FILE_TOO_LARGE" }` |
| `422 Unprocessable Entity` | Conversion failed (both converters) | `ApiErrorResponse { error_code: "CONVERSION_FAILED" }` |
| `422 Unprocessable Entity` | Image-only PDF (no text output) | `ApiErrorResponse { error_code: "IMAGE_ONLY_PDF" }` |
| `500 Internal Server Error` | Unexpected server exception | `ApiErrorResponse { error_code: "INTERNAL_ERROR" }` |
| `503 Service Unavailable` | Concurrent job limit reached | `ApiErrorResponse { error_code: "SERVER_BUSY" }` |
| `504 Gateway Timeout` | Conversion exceeded 60s timeout | `ApiErrorResponse { error_code: "CONVERSION_TIMEOUT" }` |

**Example success response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "quarterly_report.docx",
  "file_size_bytes": 204800
}
```

**Example error response:**
```json
{
  "error_code": "FILE_TOO_LARGE",
  "message": "Uploaded file exceeds the maximum allowed size of 50 MB.",
  "detail": "Received 63,217,445 bytes; limit is 52,428,800 bytes."
}
```

---

#### `GET /api/download/{job_id}`

**Request:**

| Property | Value |
|----------|-------|
| Method | `GET` |
| Path | `/api/download/{job_id}` |
| Auth | None |

| Parameter | Type | Required | Constraints |
|-----------|------|----------|-------------|
| `job_id` | Path string | Yes | UUID v4 regex: `[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}` |

**Responses:**

| Status | Condition | Body / Headers |
|--------|-----------|----------------|
| `200 OK` | DOCX ready for download | Binary DOCX stream; `Content-Disposition: attachment; filename="..."` |
| `202 Accepted` | Job still converting | `{ "status": "converting" }` |
| `400 Bad Request` | `job_id` fails UUID v4 format | `ApiErrorResponse { error_code: "INVALID_JOB_ID" }` |
| `404 Not Found` | Unknown, expired, or already-downloaded `job_id` | `ApiErrorResponse { error_code: "JOB_NOT_FOUND" }` |
| `410 Gone` | Job previously failed | `ApiErrorResponse { error_code: "JOB_FAILED" }` |
| `500 Internal Server Error` | Job registry/disk inconsistency | `ApiErrorResponse { error_code: "INTERNAL_ERROR" }` |

**Success response headers:**
```
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="quarterly_report.docx"
Content-Length: 204800
Cache-Control: no-store
```

---

#### `GET /api/health`

**Request:**

| Property | Value |
|----------|-------|
| Method | `GET` |
| Path | `/api/health` |
| Auth | None |

**Response (200 OK):**
```json
{
  "status": "ok",
  "temp_dir_writable": true,
  "active_jobs": 2
}
```

---

### 4.4 Error Catalog

| Error Code | HTTP Status | Trigger | User-Facing Message |
|------------|-------------|---------|---------------------|
| `INVALID_FILE_TYPE` | 400 | Magic bytes ≠ `%PDF`; or MIME ≠ `application/pdf` | "This file doesn't appear to be a valid PDF." |
| `FILE_TOO_LARGE` | 413 | Byte count > 52,428,800 | "Your file is too large to convert." |
| `CONVERSION_TIMEOUT` | 504 | Job killed after `JOB_TIMEOUT_SECONDS` | "Conversion took too long and was cancelled." |
| `CONVERSION_FAILED` | 422 | Both pdf2docx and LibreOffice raised exceptions | "We couldn't convert this PDF." |
| `IMAGE_ONLY_PDF` | 422 | Output DOCX contains zero text paragraphs | "This PDF contains only images and cannot be converted." |
| `SERVER_BUSY` | 503 | Active jobs ≥ `MAX_CONCURRENT_JOBS` | "The server is busy. Please try again in a moment." |
| `INTERNAL_ERROR` | 500 | Unexpected exception | "Something went wrong on our end." |
| `JOB_NOT_FOUND` | 404 | Unknown/expired/already-downloaded `job_id` | "Your conversion result has expired." |
| `JOB_FAILED` | 410 | `job_id` exists but state is `FAILED` | "The conversion failed. Please try again." |
| `INVALID_JOB_ID` | 400 | `job_id` fails UUID v4 regex | "Invalid download link." |

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

PDFConverter is an **anonymous-access** application. There are no user accounts, sessions, or tokens. Security is achieved through input validation, resource limits, and ephemeral file handling rather than identity controls.

### 5.2 File Upload Security

| Control | Implementation | Requirement |
|---------|----------------|-------------|
| Magic byte validation | Read first 8 bytes; check `25 50 44 46` (`%PDF`) | MUST — before any disk write |
| MIME type check | Validate `Content-Type: application/pdf` header | Secondary check (after magic bytes) |
| Hard size cap | Track byte count during read; reject on `> MAX_FILE_SIZE_BYTES` | MUST — server-side, not extension-only |
| Early rejection | Check `Content-Length` header before reading body | SHOULD — saves bandwidth |
| No original filename on disk | UUID v4 used as on-disk filename exclusively | MUST — prevents path traversal |
| File permissions | `600` for files, `700` for job directories | MUST — owner read/write only |
| No shell execution | Upload file path passed to Python library only; never via `shell=True` | MUST |
| No filename in subprocess | LibreOffice fallback uses `job_id` path, not original filename | MUST |

### 5.3 Path Traversal Prevention

All file system operations use the pattern:

```python
import os
import uuid

job_id = str(uuid.uuid4())
job_dir = os.path.join(settings.TEMP_DIR, job_id)           # /tmp/pdfconverter/{uuid}
pdf_path = os.path.join(job_dir, f"{job_id}.pdf")           # /tmp/pdfconverter/{uuid}/{uuid}.pdf
docx_path = os.path.join(job_dir, f"{job_id}.docx")         # /tmp/pdfconverter/{uuid}/{uuid}.docx
```

The original filename is **never** used in any `os.path` operation. It is stored only in the in-memory `JobRecord.original_filename` field for filename derivation.

### 5.4 Resource Exhaustion Prevention

| Control | Mechanism | Default |
|---------|-----------|---------|
| File size limit | Hard cap on upload bytes | 50 MB |
| Conversion timeout | Thread watchdog / `subprocess` timeout | 60 seconds |
| Concurrent job limit | Atomic counter in `JobRegistry`; reject with `503` at limit | 5 simultaneous jobs |
| TTL sweep | Background task deletes orphaned temp dirs | 60-minute TTL, 10-minute sweep |

### 5.5 Privacy & No-Persistence Policy

| Requirement | Implementation |
|-------------|---------------|
| No permanent file storage | All I/O in `TEMP_DIR`; no database writes; no cloud storage |
| Immediate post-download deletion | Async callback after `StreamingResponse` last byte sent |
| Immediate failure cleanup | `finally` block in `ConversionService` deletes job dir on any exception |
| TTL safety net | `cleanup.py` sweep for orphaned files |
| No content logging | Log lines include only: `job_id`, `duration_ms`, `outcome`, `file_size_bytes` |
| No original filename in logs | `original_filename` never written to log output |
| Single-download enforcement | After download, job state is `DOWNLOADED` and files are deleted; repeat `GET` returns `404` |

### 5.6 Transport Security

- All traffic served over HTTPS (TLS termination at PaaS edge or load balancer)
- `Cache-Control: no-store` on all download responses to prevent proxy caching
- CORS restricted to configured `ALLOWED_ORIGINS` (default `*` for public API; tighten for production)

### 5.7 Content Security Policy

Frontend `index.html` should include:

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'">
```

This restricts all resource loading to same origin and prevents XSS via injected scripts.

---

## 6. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Runtime** | Python | 3.11+ | Server runtime |
| **Web Framework** | FastAPI | 0.111+ | ASGI API server; automatic OpenAPI; streaming responses |
| **ASGI Server** | Uvicorn | 0.29+ | Production ASGI server; runs FastAPI |
| **Validation** | Pydantic v2 | 2.x | Request/response schema validation; `pydantic-settings` for config |
| **Primary Converter** | pdf2docx | 0.5.x | PDF parsing and DOCX reconstruction |
| **DOCX Manipulation** | python-docx | 1.x | Read output DOCX to detect image-only PDFs |
| **Fallback Converter** | LibreOffice headless | 7.x | Fallback PDF-to-DOCX conversion via subprocess |
| **Background Tasks** | APScheduler (or asyncio) | 3.x | TTL sweep scheduling |
| **Frontend** | Vanilla HTML/CSS/JS | — | No framework; minimal bundle size |
| **Static Serving** | FastAPI `StaticFiles` (dev) / Nginx (prod) | — | Serve `index.html`, `app.js`, `styles.css` |
| **Containerisation** | Docker | 24+ | Optional; recommended for consistent LibreOffice environment |

### 6.1 Dependency Licenses

| Library | License | Notes |
|---------|---------|-------|
| `fastapi` | MIT | No restrictions |
| `uvicorn` | BSD | No restrictions |
| `pydantic` | MIT | No restrictions |
| `pdf2docx` | MIT | No restrictions |
| `python-docx` | MIT | No restrictions |
| LibreOffice | MPL 2.0 | Open source; distribution allowed |

All dependencies are MIT/BSD/MPL — no copyleft conflicts for a web service deployment.

### 6.2 Python Package Requirements (`requirements.txt`)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.9   # Required by FastAPI for multipart/form-data
pdf2docx>=0.5.6
python-docx>=1.1.0
apscheduler>=3.10.0
```

### 6.3 System Dependencies

```
# Required in container / server environment
libreoffice-writer   # LibreOffice headless fallback converter
```

---

## 7. Integration Points

### 7.1 pdf2docx (Primary Conversion Library)

| Attribute | Detail |
|-----------|--------|
| Type | Python library (in-process) |
| Package | `pdf2docx` on PyPI |
| Usage | `from pdf2docx import Converter` |
| Invocation | `cv = Converter(pdf_path); cv.convert(docx_path); cv.close()` |
| Threading | Invoked in a `concurrent.futures.ThreadPoolExecutor` thread with `JOB_TIMEOUT_SECONDS` deadline |
| Error handling | Catches all exceptions; triggers LibreOffice fallback |
| Limitations | Does not support image-only (scanned) PDFs; complex layouts may have fidelity loss |

**Invocation pattern:**
```python
import concurrent.futures
from pdf2docx import Converter

def _run_pdf2docx(pdf_path: str, docx_path: str) -> None:
    cv = Converter(pdf_path)
    try:
        cv.convert(docx_path, start=0, end=None)
    finally:
        cv.close()

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(_run_pdf2docx, pdf_path, docx_path)
    try:
        future.result(timeout=settings.JOB_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError:
        raise ConversionTimeoutError()
    except Exception as e:
        raise ConversionLibraryError(str(e))
```

---

### 7.2 LibreOffice Headless (Fallback Converter)

| Attribute | Detail |
|-----------|--------|
| Type | External process (subprocess) |
| Binary | `libreoffice` (must be on `PATH` in server environment) |
| Invocation | `subprocess.run(["libreoffice", "--headless", "--convert-to", "docx", pdf_path, "--outdir", job_dir], timeout=JOB_TIMEOUT_SECONDS)` |
| Error handling | Non-zero return code or `subprocess.TimeoutExpired` → `ConversionFailedError` |
| Security | Path arguments use `job_id`-based paths only; `shell=False` always |
| Availability | Optional — service degrades gracefully if LibreOffice not installed (only `pdf2docx` used) |

---

### 7.3 Operating System Filesystem

| Attribute | Detail |
|-----------|--------|
| Type | Local ephemeral filesystem |
| Path | Configurable via `TEMP_DIR` env var (default `/tmp/pdfconverter`) |
| Operations | `os.makedirs`, `open()` write, `os.stat()`, `shutil.rmtree()`, `os.scandir()` |
| Permissions | Directories: `700`; Files: `600` |
| Durability | Ephemeral — contents lost on server restart; by design |
| Monitoring | TTL sweep logs byte count and directory count of orphaned files removed |

---

### 7.4 Browser File APIs (Frontend Integration)

| API | Usage |
|-----|-------|
| `<input type="file">` | File picker for PDF selection |
| `DataTransfer` / drag events | Drag-and-drop file selection |
| `File.type`, `File.name`, `File.size` | Client-side pre-upload validation |
| `XMLHttpRequest` + `upload.onprogress` | Upload progress events for the progress bar |
| `fetch` | `GET /api/download/{job_id}` call |
| `URL.createObjectURL` / `<a download>` | Trigger browser file download from response |

---

### 7.5 External Services (None for v1)

PDFConverter has **no external service dependencies** in v1:

| Service | Status | Notes |
|---------|--------|-------|
| Database | ❌ Not used | In-memory job registry only |
| Redis / cache | ❌ Not used | Upgrade path if multi-process scaling needed |
| Cloud storage (S3, GCS) | ❌ Not used | Ephemeral filesystem only; by design |
| Email / notifications | ❌ Not used | No user accounts |
| CDN | ⚠️ Optional | Static assets can be fronted by CDN if traffic warrants |
| Monitoring (Sentry, Datadog) | ⚠️ Optional | Recommended for production but not required for MVP |

---

*Document generated: 2026-05-12 | Project: PDFConverter | Version: 1.0*
*Based on: PRD-PDFConverter.md v1.0 · FRD-PDFConverter.md v1.0*
