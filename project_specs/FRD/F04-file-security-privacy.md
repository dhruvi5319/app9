---

## F04: File Security & Privacy Controls

**Description:** Because users upload potentially sensitive personal and professional documents, the application enforces a strict no-persistence policy and implements multiple layers of defence against malicious input. Files are validated server-side before being written to disk, stored only in an isolated temp directory under UUID-based filenames, and deleted as soon as the conversion transaction completes. A TTL-based background sweep removes orphaned files that were never explicitly cleaned up (e.g., from aborted sessions or server crashes). No file content or user-identifying metadata is logged.

---

### Terminology

- **No-Persistence Policy:** The rule that no uploaded or converted file is ever written to long-term (persistent) storage. All file I/O occurs in a designated temp directory and is transient by design.
- **Isolated Temp Directory:** A dedicated directory (e.g., `/tmp/pdfconverter/`) used exclusively by this application for transient file storage. Each job gets its own subdirectory (`{TEMP_DIR}/{job_id}/`).
- **TTL Sweep:** A background cleanup process (cron job or startup task) that scans the temp directory and deletes any subdirectory older than the configured TTL (default: 60 minutes). Handles orphaned files from crashed jobs or abandoned sessions.
- **Orphaned File:** A temp file that was never cleaned up by the normal post-download workflow (F02) because the client disconnected, the server crashed, or the download was never requested.
- **MIME Inspection:** Server-side verification of the true file type by reading magic bytes from the file content, independent of the filename extension or the `Content-Type` HTTP header declared by the client.
- **Path Traversal:** An attack where a malicious filename (e.g., `../../etc/passwd`) causes the server to read or write outside the intended directory. Mitigated by using only the `job_id` (UUID) as the on-disk filename.
- **Concurrent Job Limit:** A configured maximum number of simultaneous active conversion jobs. New submissions beyond this limit receive `503 SERVER_BUSY`.

---

### Sub-features

- Server-side MIME type inspection (magic bytes, not extension-only)
- Configurable maximum file size enforcement at server boundary
- UUID-based temp file naming (no original filename used on disk)
- File permission hardening (temp files written as `600`, directories as `700`)
- Post-download immediate deletion of both source PDF and output DOCX
- On-failure immediate deletion of any written temp files
- TTL-based background sweep for orphaned files (60-minute default)
- No logging of file contents or document metadata
- Concurrent job limit to prevent resource exhaustion
- Sandbox: conversion library invoked as isolated process (no shell execution of uploaded content)

---

### Process

**A. Per-Request Security (synchronous, every upload):**
1. Receive upload request at `POST /api/convert`.
2. Check `Content-Length` header (if present); reject immediately if > 52,428,800 bytes.
3. Begin reading body; track running byte count.
4. After reading first 8 bytes, validate magic bytes (`%PDF`). If invalid → discard body, return `400 INVALID_FILE_TYPE`.
5. Continue reading body; if running byte count exceeds 52,428,800 → stop reading, return `413 FILE_TOO_LARGE`.
6. Generate `job_id` (UUID v4).
7. Create directory `{TEMP_DIR}/{job_id}/` with permissions `700`.
8. Write file as `{TEMP_DIR}/{job_id}/{job_id}.pdf` with permissions `600`.
9. Proceed with conversion (F01).
10. On **failure**: delete `{TEMP_DIR}/{job_id}/` and all contents immediately.
11. On **success**: retain files for download (F02). Delete after download confirmed or TTL expires.

**B. TTL Background Sweep (periodic, autonomous):**
1. The sweep runs on a configurable schedule (default: every 10 minutes).
2. List all subdirectories of `{TEMP_DIR}/`.
3. For each subdirectory, check the directory creation timestamp (or a `created_at` metadata file).
4. If `now - created_at > TTL` (default 60 minutes) → delete the subdirectory and all contents.
5. Log the count of directories swept and bytes freed (no file content or identifying info logged).

**C. Concurrent Job Control:**
1. Maintain a server-side counter of active conversion jobs (in-process atomic integer or Redis counter).
2. Before accepting a new job (step 7 of Process A), check if counter ≥ configured limit (default: 5 concurrent).
3. If at limit → return `503 SERVER_BUSY` with error code `SERVER_BUSY`.
4. Increment counter when job is accepted; decrement when job completes (success, failure, or timeout).

---

### Inputs

- Uploaded file bytes (from `POST /api/convert`)
- `Content-Length` HTTP header (optional, used for early rejection)
- `Content-Type` HTTP header (used as secondary MIME check, not primary)
- Directory listing of `{TEMP_DIR}/` (for TTL sweep)
- Directory creation timestamps or `created_at` marker files (for TTL age calculation)

---

### Outputs

- Validated, UUID-named temp files written to isolated directory (on success of validation)
- HTTP `400`/`413`/`503` error responses (on rejection — no files written)
- Deletion of temp directory and contents (on job completion or TTL expiry)
- Sweep log entry: count of directories deleted, bytes freed (no content/metadata)

---

### Validation Rules

- **MUST** inspect magic bytes server-side for every upload, regardless of declared MIME type.
- **MUST** reject files whose first 4 bytes are not `25 50 44 46` (`%PDF`).
- **MUST** enforce 50 MB limit server-side, regardless of client-side validation.
- **MUST** use UUID v4 as the on-disk filename for all temp files (never the original filename).
- **MUST** set temp file permissions to `600` and temp directory permissions to `700`.
- **MUST** delete temp files immediately on any conversion failure.
- **MUST** delete temp files after successful download delivery.
- **MUST** run TTL sweep to delete orphaned files older than 60 minutes.
- **MUST NOT** log file content, original filename, or any user-identifying metadata.
- **MUST NOT** pass the original filename to any shell command (prevents shell injection).
- **MUST NOT** execute uploaded file content; only pass the file path to the conversion library.
- **MUST** limit concurrent active conversion jobs (default: 5).
- **SHOULD** store `TEMP_DIR`, `MAX_FILE_SIZE_BYTES`, `JOB_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, and `TTL_MINUTES` as configurable environment variables.
- **MUST NOT** serve any temp file via a guessable or sequential URL (UUID v4 provides sufficient entropy).

---

### Error States

| Scenario | HTTP Status | Error Code | Description |
|----------|-------------|------------|-------------|
| File fails magic byte check | 400 | `INVALID_FILE_TYPE` | Not a valid PDF by content |
| File exceeds 50 MB server-side | 413 | `FILE_TOO_LARGE` | Hard server limit exceeded |
| Concurrent job limit reached | 503 | `SERVER_BUSY` | Queue at capacity |
| Temp dir write failure (disk full) | 500 | `INTERNAL_ERROR` | Cannot write to temp directory |

---

### Configuration Reference

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `TEMP_DIR` | `/tmp/pdfconverter` | Root temp directory for all jobs |
| `MAX_FILE_SIZE_BYTES` | `52428800` | Hard upload size cap (50 MB) |
| `JOB_TIMEOUT_SECONDS` | `60` | Per-job conversion timeout |
| `MAX_CONCURRENT_JOBS` | `5` | Max simultaneous active conversions |
| `TTL_MINUTES` | `60` | Orphaned file TTL before sweep deletes |
| `SWEEP_INTERVAL_MINUTES` | `10` | How often the TTL sweep runs |

---

### API Surface (this feature)

No new endpoints. Security controls apply to `POST /api/convert` (see `Y1-api.md`). The TTL sweep is a server-internal process with no API surface.

---

### Schema Surface (this feature)

Temp directory layout and job state registry. See `Y0-schema.md` for full schema.

---
