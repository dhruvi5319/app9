# Functional Requirements Document
# PDF to DOCX Converter (PDFConverter)

**Version:** 1.0
**Date:** 2026-05-11
**Status:** Draft
**Based on:** PRD-PDFConverter.md v1.0

---

## Scope

This document defines the complete functional specification for the PDFConverter web application — a minimal, no-account browser-based tool that converts PDF files to editable DOCX (Microsoft Word) format. It covers all five MVP features (F0–F4), the REST API surface, temporary file storage schema, cross-feature error catalog, and external integration points.

This FRD is authoritative. Downstream implementation agents must treat it as the single source of truth for feature behaviour, validation rules, input/output contracts, and error handling.

---

## How to Read This Document

- **Feature IDs** follow `F{nn}` notation (zero-padded). Each feature chunk is self-contained.
- **API endpoints** are summarised inline per feature and fully specified in `Y1-api.md`.
- **Storage schema** is summarised inline per feature and fully specified in `Y0-schema.md`.
- **Error codes** are referenced inline and catalogued in `Y2-errors.md`.
- **External integrations** are described in `Y3-integrations.md`.
- All HTTP status codes follow RFC 9110.
- All file size references use binary megabytes (1 MB = 1,048,576 bytes) unless otherwise stated.

---

## Table of Contents

| Section | Description |
|---------|-------------|
| [F00 – File Upload Interface](#f00-file-upload-interface) | Browser upload UI, drag-and-drop, client-side validation |
| [F01 – Server-Side PDF-to-DOCX Conversion](#f01-server-side-pdf-to-docx-conversion) | Core conversion engine, temp storage, timeout |
| [F02 – DOCX File Download](#f02-docx-file-download) | Download delivery, filename mapping, cleanup |
| [F03 – User Feedback & Status Communication](#f03-user-feedback--status-communication) | Progress indicators, status messages, retry flow |
| [F04 – File Security & Privacy Controls](#f04-file-security--privacy-controls) | Input validation, no-persistence policy, TTL cleanup |
| [Y0 – Storage Schema](#y0-storage-schema) | Temp directory layout and job metadata |
| [Y1 – API Endpoints](#y1-api-endpoints) | Full REST API specification |
| [Y2 – Error Catalog](#y2-error-catalog) | Cross-feature error codes and HTTP statuses |
| [Y3 – Integrations](#y3-integrations) | External library and system dependencies |

---

## Cross-Cutting Terminology

| Term | Definition |
|------|-----------|
| **PDF** | Portable Document Format file (`.pdf`). The source file uploaded by the user. |
| **DOCX** | Microsoft Word Open XML document format (`.docx`). The output file returned to the user. |
| **Conversion Job** | The server-side lifecycle of a single PDF upload: receive → validate → convert → deliver → clean up. |
| **Temp Directory** | An isolated, server-managed directory (e.g., `/tmp/pdfconverter/`) where uploaded PDFs and generated DOCX files are stored transiently during a conversion job. |
| **Job ID** | A server-generated UUID (v4) uniquely identifying a single conversion job and its associated temp files. |
| **TTL** | Time-To-Live. The maximum duration a temp file may exist on the server before being swept by the cleanup job (default: 60 minutes). |
| **MIME Type** | Media type string (e.g., `application/pdf`) used for server-side file type validation. |
| **Client-Side Validation** | Validation performed in the browser before the upload request is sent. Acts as a UX guard, not a security boundary. |
| **Server-Side Validation** | Authoritative validation performed on the server after receiving the upload. The security boundary. |
| **Orphaned File** | A temp file whose parent conversion job was abandoned (e.g., client disconnected mid-upload) and which was never explicitly cleaned up by the normal workflow. Handled by the TTL sweep. |
| **Image-only PDF** | A PDF whose pages consist entirely of rasterised images with no extractable text layer. Cannot be converted by `pdf2docx` without OCR (out of scope for v1). |

---

## Conventions

- **Required fields** are marked `(required)`.
- **Optional fields** are marked `(optional)`.
- Validation rules use the word **MUST** (mandatory), **SHOULD** (strongly recommended), and **MAY** (permitted but not required).
- Error code format: `UPPER_SNAKE_CASE` string returned in JSON error body.
- All timestamps are ISO 8601 UTC.

---
---

## F00: File Upload Interface

**Description:** The File Upload Interface is the primary user entry point — the only page of the application. It presents a clean, minimal HTML page with a file selection control that accepts a single PDF file via either a file picker dialog or drag-and-drop onto a designated drop zone. The interface performs immediate client-side validation (type and size) before transmitting the file to the server, and provides real-time visual feedback during upload via a progress bar. A "Convert to DOCX" button initiates the conversion workflow.

---

### Terminology

- **Drop Zone:** A visually designated `<div>` region on the page that accepts PDF files dragged from the desktop or file manager.
- **File Picker:** The native OS file dialog opened by `<input type="file">` accepting `.pdf` files.
- **Upload Progress Bar:** A visual HTML element (e.g., `<progress>` or styled `<div>`) reflecting bytes uploaded vs. total, updated via `XMLHttpRequest` or `fetch` progress events.
- **Convert Button:** The primary CTA button labelled "Convert to DOCX" that submits the upload request. Disabled until a valid file is selected.

---

### Sub-features

- Single PDF file selection via file picker (`<input type="file" accept=".pdf,application/pdf">`)
- Drag-and-drop upload onto a designated drop zone
- Client-side file type validation (MIME type and `.pdf` extension)
- Client-side file size guard (reject before upload if file exceeds configured limit)
- Upload progress indicator (progress bar updated during transmission)
- "Convert to DOCX" CTA button (disabled until valid file selected; spinner while uploading)
- Selected filename display (show chosen filename and size to user before upload)
- Reset / clear selection (allow user to pick a different file before converting)

---

### Process

1. User lands on the application's single-page UI.
2. User selects a PDF file via the file picker dialog **OR** drags a file onto the drop zone.
3. **Client-side type check:** Browser inspects `file.type` (MIME) and `file.name` extension.
   - If not `.pdf` / `application/pdf` → display inline error "Please select a PDF file." Do not enable Convert button.
4. **Client-side size check:** Browser compares `file.size` against the configured maximum (50 MB = 52,428,800 bytes).
   - If file exceeds limit → display inline error "File too large. Maximum size is 50 MB." Do not enable Convert button.
5. If both checks pass → display the selected filename and file size; enable the "Convert to DOCX" button.
6. User clicks "Convert to DOCX".
7. UI disables the button, shows a spinner on the button label, and initialises the upload progress bar at 0%.
8. Browser opens an HTTP `POST /api/convert` multipart request with the file attached.
9. Upload progress events update the progress bar (0–100%) as bytes are transmitted.
10. On completion of the upload the UI transitions to the "Converting…" status indicator (see F03).
11. (Server processing continues — see F01.)

---

### Inputs

- `file` (File object, required): The PDF file selected by the user.
  - Must have MIME type `application/pdf` (client check: `file.type`)
  - Must have `.pdf` file name extension (client check: `file.name.endsWith('.pdf')`)
  - Must not exceed 52,428,800 bytes / 50 MB (client check: `file.size`)

---

### Outputs

- **On valid file selection:** Filename label and size badge rendered in UI; "Convert to DOCX" button enabled.
- **On invalid type:** Inline error message "Please select a PDF file."; button remains disabled.
- **On invalid size:** Inline error message "File too large. Maximum size is 50 MB."; button remains disabled.
- **On upload initiation:** Button enters loading state (disabled + spinner); progress bar visible at 0%.
- **During upload:** Progress bar updates continuously from 0% to 100% as bytes are sent.
- **On upload complete:** UI transitions to "Converting…" state (handled by F03).

---

### Validation Rules

- **MUST** accept only files whose MIME type is `application/pdf` (client-side check on `file.type`).
- **MUST** also check that the filename ends with `.pdf` (case-insensitive) as a secondary client check.
- **MUST** reject files larger than 50 MB before upload begins.
- **MUST** disable the "Convert to DOCX" button until a file passing both checks is selected.
- **MUST** reset validation state and re-run checks if the user changes the selected file.
- **SHOULD** support drag-and-drop in addition to file picker (applies same validation on `drop` event).
- **MUST** prevent default browser drag-over behaviour (file being opened in a new tab) on drag enter/over/drop events.
- **MUST** display human-readable file size (e.g., "12.3 MB") alongside the filename after selection.
- **MUST** be fully keyboard navigable: file picker activatable by `Enter`/`Space`, Convert button focusable and activatable by `Enter`.

---

### Error States

| Scenario | Trigger | UI Message | Button State |
|----------|---------|------------|--------------|
| Non-PDF file selected | `file.type ≠ application/pdf` or extension ≠ `.pdf` | "Please select a PDF file." | Disabled |
| File too large | `file.size > 52,428,800` | "File too large. Maximum size is 50 MB." | Disabled |
| No file selected on submit | User attempts submit without selection | "Please select a PDF file first." | Disabled |
| Upload network failure | XHR/fetch rejects with network error | Transition to F03 error state: "Upload failed. Please check your connection and try again." | Reset to enabled |

---

### API Surface (this feature)

This feature initiates `POST /api/convert`. See `Y1-api.md §POST /api/convert` for full request/response schema.

---

### Schema Surface (this feature)

No database tables. File is transmitted directly to the server in a multipart POST. Server assigns a `job_id` and writes the file to the temp directory (see `Y0-schema.md §Temp Directory Layout`).

---
---

## F01: Server-Side PDF-to-DOCX Conversion

**Description:** The core processing engine of the application. When the server receives a valid PDF upload via `POST /api/convert`, it performs authoritative server-side validation of the file (MIME type, size, content integrity), writes the file to an isolated temp directory, and invokes `pdf2docx` to perform the conversion. The resulting DOCX file is stored in the same temp directory under the same job ID. The server enforces a hard per-job timeout to prevent runaway conversions from consuming server resources. On success, the server returns the job ID to the client for download retrieval. On failure, a structured error response is returned.

---

### Terminology

- **Conversion Library:** `pdf2docx` (primary) — a Python library that uses `pdfminer` and `python-docx` to parse PDF structure and reconstruct it as a DOCX file. LibreOffice headless is the fallback.
- **LibreOffice Headless:** LibreOffice running in non-GUI mode, invoked via subprocess as a fallback converter when `pdf2docx` fails.
- **Job Timeout:** The maximum wall-clock time allowed for a single conversion before the server terminates the job and returns an error. Default: 60 seconds.
- **Magic Bytes:** The first few bytes of a file that identify its true format (e.g., PDF files begin with `%PDF`). Used for server-side MIME validation independent of filename or declared content-type.
- **Image-Only PDF:** A PDF whose content is entirely raster images with no text layer. `pdf2docx` will produce an empty or near-empty DOCX for these files.
- **Temp File Pair:** The two files associated with a conversion job: `{job_id}.pdf` (source) and `{job_id}.docx` (output).

---

### Sub-features

- Server-side file type validation (magic bytes + MIME header inspection)
- Server-side file size enforcement (hard cap at 50 MB)
- Secure temp file write (UUID-named file in isolated temp directory)
- PDF-to-DOCX conversion via `pdf2docx` (primary)
- Fallback conversion via LibreOffice headless (if `pdf2docx` raises an exception)
- Per-job conversion timeout enforcement (60 seconds default)
- Image-only PDF detection (detect empty/near-empty DOCX output; surface specific error)
- Structured JSON success/error response
- Temp file cleanup on conversion failure

---

### Process

1. Server receives `POST /api/convert` with `multipart/form-data` body containing the uploaded file.
2. **Server-side type validation:**
   - Read the first 8 bytes of the uploaded stream and check for `%PDF` magic bytes.
   - Inspect declared `Content-Type` header for `application/pdf`.
   - If either check fails → return `400 BAD_REQUEST` with error code `INVALID_FILE_TYPE`; do not write file to disk.
3. **Server-side size validation:**
   - Inspect `Content-Length` header (if present) before reading body.
   - After reading, verify actual byte count ≤ 52,428,800 bytes.
   - If exceeded → return `413 REQUEST_ENTITY_TOO_LARGE` with error code `FILE_TOO_LARGE`; discard received bytes.
4. **Generate Job ID:** Server generates a UUID v4 (`job_id`).
5. **Write source file:** Save uploaded bytes to `{TEMP_DIR}/{job_id}/{job_id}.pdf` with file permissions `600`.
6. **Invoke conversion (primary — `pdf2docx`):**
   - Call `pdf2docx.parse(source_path, output_path)` inside a subprocess or thread with a 60-second timeout watchdog.
   - If timeout expires → kill process/thread; return `504 GATEWAY_TIMEOUT` with error code `CONVERSION_TIMEOUT`; delete temp files.
   - If `pdf2docx` raises an exception → attempt fallback (step 7).
   - If `pdf2docx` succeeds → proceed to step 8.
7. **Fallback — LibreOffice headless (if `pdf2docx` failed):**
    - Invoke LibreOffice in headless/non-GUI mode to convert the source PDF to DOCX format, writing the output to the same job directory. Apply the same 60-second timeout as the primary converter.
    - If fallback also fails or times out → return `422 UNPROCESSABLE_ENTITY` with error code `CONVERSION_FAILED`; delete temp files.
8. **Image-only PDF detection:**
    - Inspect output DOCX: if it contains zero paragraphs whose stripped text content has a character length > 0 (i.e., no paragraph contains any non-whitespace characters) → return `422 UNPROCESSABLE_ENTITY` with error code `IMAGE_ONLY_PDF`; delete temp files.
    - Note: empty table cells, whitespace-only paragraphs, and paragraphs containing only line-break runs do **not** count as text content for this check.
9. **Success:** Return `200 OK` JSON response containing `job_id` and `filename` (derived from original filename).
10. **Temp files retained** at `{TEMP_DIR}/{job_id}/` for download by the client (see F02). Subject to TTL sweep after 60 minutes.

---

### Inputs

- `file` (multipart file field, required): The uploaded PDF file.
  - Declared MIME type: `application/pdf`
  - Magic bytes: file content MUST begin with `%PDF`
  - Max size: 52,428,800 bytes (50 MB)
- `Content-Length` (HTTP header, optional): Byte count of the request body. Checked pre-read if present.
- `Content-Type` (HTTP header, required): Must be `multipart/form-data` with boundary.
- `original_filename` (derived from `Content-Disposition` of the file part, required): Used to derive the DOCX output filename.

---

### Outputs

**On success (`200 OK`):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "report.docx",
  "file_size_bytes": 204800
}
```

**On failure:** See `Y2-errors.md` for full error response schema and all error codes.

---

### Validation Rules

- **MUST** validate MIME type server-side using magic bytes, regardless of declared `Content-Type`.
- **MUST** reject any file not beginning with `%PDF` magic bytes.
- **MUST** reject any file exceeding 52,428,800 bytes.
- **MUST** assign a UUID v4 `job_id` to every accepted job before writing to disk.
- **MUST** write source files to `{TEMP_DIR}/{job_id}/{job_id}.pdf` (not using original filename to prevent path traversal).
- **MUST** set file permissions to `600` (owner read/write only) on written temp files.
- **MUST** enforce a 60-second hard timeout on the conversion process.
- **MUST** delete all temp files for a job on any conversion failure before returning the error response.
- **MUST** detect image-only PDFs (zero text in output) and return `IMAGE_ONLY_PDF` error rather than serving an empty DOCX.
- **SHOULD** log conversion duration and outcome (without logging file content or user-identifying metadata).
- **MUST NOT** execute or interpret uploaded file content in any way other than passing it to the conversion library.
- **MUST NOT** use the original filename when writing to disk (use `job_id` as the on-disk filename).

---

### Error States

| Scenario | HTTP Status | Error Code | Description |
|----------|-------------|------------|-------------|
| File is not a PDF (magic bytes) | 400 | `INVALID_FILE_TYPE` | File does not begin with `%PDF` |
| Declared MIME not `application/pdf` | 400 | `INVALID_FILE_TYPE` | Content-Type header check failed |
| File exceeds 50 MB | 413 | `FILE_TOO_LARGE` | Server byte count exceeds limit |
| Conversion timeout (>60s) | 504 | `CONVERSION_TIMEOUT` | Job killed after 60s |
| `pdf2docx` and LibreOffice both fail | 422 | `CONVERSION_FAILED` | Both converters raised exceptions |
| Output DOCX has no text content | 422 | `IMAGE_ONLY_PDF` | Likely scanned/image-only PDF |
| Server internal error | 500 | `INTERNAL_ERROR` | Unexpected server-side exception |
| Too many concurrent jobs | 503 | `SERVER_BUSY` | Conversion queue at capacity |

---

### API Surface (this feature)

`POST /api/convert` — see `Y1-api.md §POST /api/convert` for full multipart request schema and response shapes.

---

### Schema Surface (this feature)

Uses temp directory layout: `{TEMP_DIR}/{job_id}/{job_id}.pdf` and `{TEMP_DIR}/{job_id}/{job_id}.docx`. Optional in-memory job registry (Python dict or Redis) tracks job state. See `Y0-schema.md §Job State` for full schema.

---
---

## F02: DOCX File Download

**Description:** Upon successful conversion (F01 returns a `job_id`), the application immediately delivers the converted DOCX file to the user's browser as a file download. The file is served under a meaningful name derived from the original PDF filename. After the download response body has been fully transmitted, the server deletes both the source PDF and the generated DOCX from the temp directory. A server-side TTL sweep (see F04) acts as a safety net for cases where the client disconnects before or during download, ensuring orphaned files are eventually removed.

---

### Terminology

- **Content-Disposition Header:** HTTP response header that instructs the browser to treat the response body as a file download rather than displaying it inline. Format: `Content-Disposition: attachment; filename="report.docx"`.
- **Derived Filename:** The DOCX output filename generated by stripping the `.pdf` extension from the original uploaded filename and appending `.docx` (e.g., `my_contract.pdf` → `my_contract.docx`).
- **Download Trigger:** The client behaviour that begins the file download. For v1, this is automatic: the server's response to `GET /api/download/{job_id}` causes the browser to open a Save dialog or download the file.
- **Streaming Response:** The HTTP response body is streamed from the temp file directly to the client, avoiding loading the entire DOCX into server RAM.
- **Post-Download Cleanup:** Deletion of `{TEMP_DIR}/{job_id}/` (and its contents) immediately after the response body has been fully sent.

---

### Sub-features

- Serve DOCX file as an HTTP file download (`Content-Disposition: attachment`)
- Derived filename mapping (`*.pdf` → `*.docx`)
- Streaming response (avoid buffering full file in memory)
- Post-download temp file deletion (both `.pdf` and `.docx`)
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document` header
- Job ID validation (reject download requests for unknown or expired job IDs)
- Cleanup safety net via TTL sweep (F04) for interrupted downloads

---

### Process

1. F01 returns `{ "job_id": "...", "filename": "report.docx", "file_size_bytes": N }` to the client.
2. Client (browser JS) immediately issues `GET /api/download/{job_id}`.
   - Alternatively, client renders a "Download DOCX" button that triggers this GET on click.
3. Server looks up `job_id` in the job registry.
   - If not found or already cleaned up → return `404 NOT_FOUND` with error code `JOB_NOT_FOUND`.
   - If job is still in `CONVERTING` state → return `202 ACCEPTED` with status `"converting"` (client should poll; see F03).
   - If job is in `FAILED` state → return `410 GONE` with error code `JOB_FAILED`.
4. Server locates `{TEMP_DIR}/{job_id}/{job_id}.docx`.
   - If file does not exist on disk → return `500 INTERNAL_ERROR`.
5. Server begins streaming response:
   - Status: `200 OK`
   - `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
   - `Content-Disposition: attachment; filename="{derived_filename}"`
   - `Content-Length: {file_size_bytes}`
   - Body: streamed DOCX file bytes (chunk size: 64 KB)
6. After the last byte of the response body is sent, server schedules immediate async deletion of `{TEMP_DIR}/{job_id}/` (both `.pdf` and `.docx`).
7. Server updates job registry entry to `COMPLETED` and marks files as deleted.
8. If the client disconnects before download completes, the streaming response ends; server still deletes temp files (the TTL sweep handles any race conditions — see F04).

---

### Inputs

- `job_id` (URL path parameter, required): UUID v4 string identifying the conversion job.
  - Must match pattern: `[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}`

---

### Outputs

**On success (`200 OK`):**
- Response body: raw DOCX file bytes (binary)
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `Content-Disposition: attachment; filename="{derived_filename}"`
- `Content-Length: {file_size_bytes}`

**On job not found (`404`):** JSON error body — see `Y2-errors.md §JOB_NOT_FOUND`.
**On job still converting (`202`):** JSON body `{ "status": "converting" }`.
**On job failed (`410`):** JSON error body — see `Y2-errors.md §JOB_FAILED`.

---

### Validation Rules

- **MUST** validate `job_id` format (UUID v4) before performing any file system access.
- **MUST** return `404` for any `job_id` not present in the job registry.
- **MUST** set `Content-Disposition: attachment` (never `inline`) to force browser download.
- **MUST** set the correct `Content-Type` for DOCX files.
- **MUST** derive the download filename from the original PDF filename (not from the on-disk `job_id` filename).
- **MUST** sanitise the derived filename: strip path separators (`/`, `\`), strip null bytes, limit to 255 characters.
- **MUST** delete both `.pdf` and `.docx` temp files after the response body is sent.
- **MUST** use streaming (chunked) file delivery — do not load the entire DOCX into memory.
- **SHOULD** set `Cache-Control: no-store` to prevent proxies from caching the file response.
- **MUST NOT** allow a `job_id` to be downloaded more than once (after download, job is marked `COMPLETED` and files are deleted; repeat request returns `404`).

---

### Error States

| Scenario | HTTP Status | Error Code | Description |
|----------|-------------|------------|-------------|
| Unknown or expired `job_id` | 404 | `JOB_NOT_FOUND` | No job with this ID in registry |
| Job still converting | 202 | *(no error)* | Status body: `{ "status": "converting" }` |
| Job previously failed | 410 | `JOB_FAILED` | Job errored during conversion |
| Already downloaded (files deleted) | 404 | `JOB_NOT_FOUND` | Files cleaned up post-download |
| DOCX file missing from disk | 500 | `INTERNAL_ERROR` | Job registry/disk inconsistency |
| Invalid `job_id` format | 400 | `INVALID_JOB_ID` | Fails UUID v4 regex validation |

---

### API Surface (this feature)

`GET /api/download/{job_id}` — see `Y1-api.md §GET /api/download/{job_id}` for full response headers and error schema.

---

### Schema Surface (this feature)

Reads from `{TEMP_DIR}/{job_id}/{job_id}.docx`. Updates job registry entry to `COMPLETED`. See `Y0-schema.md §Job State`.

---
---

## F03: User Feedback & Status Communication

**Description:** This feature governs all UI state transitions that keep the user informed throughout the conversion workflow. The application moves through a defined sequence of states — Idle → Uploading → Converting → Success (or Error) — each with its own visual indicators and plain-language messages. Error messages are specific, honest, and actionable. Users can retry from any error state without refreshing the page, returning the UI to the Idle state.

---

### Terminology

- **UI State Machine:** The set of mutually exclusive UI states the application can be in at any given time: `IDLE`, `UPLOADING`, `CONVERTING`, `SUCCESS`, `ERROR`.
- **Status Banner:** A visually prominent message area below the upload form that displays state-specific messages and icons.
- **Spinner:** An animated CSS/SVG indicator displayed on the Convert button and/or the status banner to signal background activity.
- **Progress Bar:** An HTML `<progress>` element (or styled equivalent) that fills from 0% to 100% as the upload progresses.
- **Retry Button:** A button in the `ERROR` state labelled "Try Again" that resets the UI to `IDLE` without a full page reload.
- **Error Detail:** A secondary, lower-emphasis text below the main error message providing the specific technical reason (e.g., "Conversion timed out after 60 seconds.").

---

### Sub-features

- Upload progress indicator (progress bar, 0–100%)
- "Converting…" status state with spinner
- Success state with download prompt / automatic download trigger
- User-friendly error messages keyed to specific error codes
- "Try Again" retry flow (soft reset to `IDLE` state)
- State machine enforcement (no invalid state transitions)

---

### UI State Machine

| State | Trigger | Visual Elements |
|-------|---------|----------------|
| `IDLE` | Page load, or "Try Again" pressed | Upload form visible; Convert button disabled until file selected |
| `UPLOADING` | User clicks "Convert to DOCX" with valid file | Progress bar 0–100%; Convert button disabled with spinner; form locked |
| `CONVERTING` | Upload reaches 100% (server acknowledged receipt) | Spinner + "Converting your document…" message; no progress bar |
| `SUCCESS` | Server returns `200` from `/api/convert`; download delivered | Green tick + "Your DOCX is ready!" message; "Download DOCX" button; link to convert another |
| `ERROR` | Any error from client-side validation, upload, server response, or failed download | Red alert icon + human-readable error message + error detail; "Try Again" button |

**Valid state transitions:**

| From | To | Trigger |
|------|----|---------|
| `IDLE` | `UPLOADING` | User clicks "Convert to DOCX" with valid file |
| `UPLOADING` | `CONVERTING` | Upload bytes fully transmitted (100%) |
| `UPLOADING` | `ERROR` | Network error during upload |
| `CONVERTING` | `SUCCESS` | Server returns `200` on `POST /api/convert` |
| `CONVERTING` | `ERROR` | Server returns `4xx` or `5xx` on `POST /api/convert` |
| `SUCCESS` | `ERROR` | `GET /api/download/{job_id}` returns error (e.g., `404 JOB_NOT_FOUND` on a second download attempt after files are deleted) |
| `SUCCESS` | `IDLE` | User clicks "Convert Another File" |
| `ERROR` | `IDLE` | User clicks "Try Again" |

No other transitions are valid. Transitions that skip states (e.g., `IDLE` → `SUCCESS`) are forbidden.

---

### Process

1. **`IDLE` state:** Page loads. Upload form is visible. Convert button is disabled.
2. User selects a valid PDF → Convert button enables (see F00).
3. User clicks "Convert to DOCX" → UI transitions to `UPLOADING`.
4. **`UPLOADING` state:** Progress bar initialised at 0%. Browser sends `POST /api/convert`.
   - XHR/fetch `progress` events update progress bar from 0% to 100%.
   - If network error occurs → transition to `ERROR` with message "Upload failed. Please check your connection and try again."
5. Upload reaches 100% (all bytes transmitted) → UI transitions to `CONVERTING`.
6. **`CONVERTING` state:** Spinner displayed. Status message: "Converting your document…"
   - Awaiting server response from `POST /api/convert` (may take up to 60 seconds).
   - No user-visible timeout on the frontend for v1 (server enforces the 60s timeout).
7. **If server returns `200`** with `job_id`:
   - Client immediately issues `GET /api/download/{job_id}`.
   - Browser receives file download response → OS download dialog opens.
   - UI transitions to `SUCCESS`.
8. **`SUCCESS` state:** Display "Your DOCX is ready!" with a green tick. Render "Convert Another File" link that returns UI to `IDLE`.
   - If the user clicks "Download DOCX" a second time after the files have already been deleted, `GET /api/download/{job_id}` returns `404 JOB_NOT_FOUND` → UI transitions from `SUCCESS` to `ERROR` with message "Your conversion result has expired."
9. **If server returns any error (4xx, 5xx):**
   - UI transitions to `ERROR`.
   - Display human-readable message mapped from error code (see Error Message Map below).
   - Display "Try Again" button.
10. **`ERROR` state:** User clicks "Try Again" → UI resets to `IDLE` (form re-enabled, progress bar hidden, error cleared, file selection reset).

---

### Error Message Map

| Error Code | User-Facing Message | Error Detail |
|------------|---------------------|--------------|
| `INVALID_FILE_TYPE` | "This file doesn't appear to be a valid PDF." | "The server was unable to verify the file as a PDF document." |
| `FILE_TOO_LARGE` | "Your file is too large to convert." | "Maximum file size is 50 MB. Please try a smaller PDF." |
| `CONVERSION_TIMEOUT` | "Conversion took too long and was cancelled." | "Large or complex PDFs may exceed the processing time limit. Try a smaller document." |
| `CONVERSION_FAILED` | "We couldn't convert this PDF." | "The document may use an unsupported format or structure. Try re-saving it from the source application." |
| `IMAGE_ONLY_PDF` | "This PDF contains only images and cannot be converted." | "Scanned or image-based PDFs require OCR, which is not supported in this version." |
| `SERVER_BUSY` | "The server is busy. Please try again in a moment." | "Too many files are being converted simultaneously." |
| `INTERNAL_ERROR` | "Something went wrong on our end." | "An unexpected server error occurred. Please try again." |
| *(Network error)* | "Upload failed. Please check your connection and try again." | *(none)* |
| `JOB_NOT_FOUND` | "Your conversion result has expired." | "The download link is no longer valid. Please convert the file again." |

---

### Inputs

- Server JSON response body from `POST /api/convert` (success or error)
- Server HTTP response from `GET /api/download/{job_id}`
- XHR/fetch upload `progress` events (bytes transmitted / total)
- User interaction events: file selection, button clicks

---

### Outputs

- Dynamic UI state transitions (DOM manipulation)
- Progress bar value updates (0–100%)
- Status banner content (message text, icon, colour coding)
- Error message and detail text rendered in the `ERROR` state
- "Download DOCX" button (visible in `SUCCESS` state)
- "Try Again" button (visible in `ERROR` state)
- "Convert Another File" link (visible in `SUCCESS` state)

---

### Validation Rules

- **MUST** map every defined server error code to a user-friendly message (see Error Message Map).
- **MUST** display a generic fallback message for any unmapped error code or unexpected HTTP status.
- **MUST** reset the file input field when the user clicks "Try Again" (clearing the previously selected file).
- **MUST** prevent state transitions that skip states (e.g., jumping from `IDLE` to `SUCCESS`) or that are not listed in the valid state transition table.
- **MUST** transition from `SUCCESS` to `ERROR` (with `JOB_NOT_FOUND` message) if `GET /api/download/{job_id}` returns a non-200 response.
- **MUST NOT** display raw error codes, stack traces, or internal server details to the user.
- **SHOULD** colour-code states: neutral/blue for progress, green for success, red for error.
- **MUST** ensure the "Try Again" button is keyboard-focusable and activatable.
- **SHOULD** announce state transitions to screen readers using ARIA live regions (`aria-live="polite"`).

---

### Error States

| Scenario | UI State | Primary Message | Action Available |
|----------|----------|----------------|-----------------|
| Any upload network error | `ERROR` | "Upload failed. Please check your connection." | Try Again |
| Server returns 4xx or 5xx | `ERROR` | Mapped message from Error Message Map | Try Again |
| Unmapped server error | `ERROR` | "Something went wrong on our end." | Try Again |
| Download link expired (404 on download) | `ERROR` | "Your conversion result has expired." | Try Again |

---

### API Surface (this feature)

Reads responses from `POST /api/convert` and `GET /api/download/{job_id}`. No new endpoints introduced. See `Y1-api.md` for full schemas.

---

### Schema Surface (this feature)

No storage. All state is maintained client-side in JavaScript. No backend schema changes.

---
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
1. The sweep runs on a configurable schedule (default: every 10 minutes). The scheduling mechanism is an implementation detail left to the implementer (e.g., a background thread, scheduled task, or startup/periodic sweep).
2. List all subdirectories of `{TEMP_DIR}/`.
3. For each subdirectory, determine its age using a reliable timestamp source (directory creation time or a `created_at` marker file written at job creation).
4. If the subdirectory age exceeds the configured TTL (default 60 minutes) → delete the subdirectory and all contents.
5. Log the count of directories deleted and bytes freed (no file content or identifying info logged).

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
