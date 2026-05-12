# Requirements Traceability Matrix
# PDF to DOCX Converter (PDFConverter)

**Version:** 1.0
**Date:** 2026-05-12
**Status:** Draft
**Based on:** PRD-PDFConverter.md v1.0 · FRD-PDFConverter.md v1.0 · TechArch-PDFConverter.md v1.0 · UserStories-PDFConverter.md v1.0

---

## Table of Contents

1. [Overview](#1-overview)
2. [Requirements Summary](#2-requirements-summary)
3. [Traceability Matrix](#3-traceability-matrix)
4. [Requirements Detail](#4-requirements-detail)
5. [Test Case Coverage](#5-test-case-coverage)
6. [Change Management](#6-change-management)
7. [Approval](#7-approval)

---

## 1. Overview

This Requirements Traceability Matrix (RTM) provides bidirectional traceability between all PDFConverter specification documents. It links every product-level feature defined in the Product Requirements Document (PRD) through to the functional requirements in the Functional Requirements Document (FRD), the technical specifications in the Technical Architecture Document (TechArch), the user stories in UserStories, and the associated test cases — ensuring every stated requirement is implemented and verifiable.

PDFConverter is a minimal, no-account web application that converts PDF files to editable DOCX (Microsoft Word) format. The product encompasses five P0 (Critical/MVP) features: file upload interface, server-side conversion, DOCX download, user feedback and status communication, and file security and privacy controls. Because every in-scope feature is load-bearing for the single user journey (upload PDF → receive DOCX), full bidirectional traceability across all five features is required before any implementation is considered complete.

The RTM serves three primary purposes. First, it provides forward traceability — confirming that each PRD feature is decomposed into FRD functional requirements, that each FRD requirement is addressed by at least one TechArch specification, and that each specification is covered by at least one user story and at least two test cases. Second, it provides backward traceability — confirming that no implementation artifact exists without a corresponding requirement, preventing scope creep. Third, it functions as a living change-impact register: when any source document changes, the RTM identifies which downstream artifacts are affected and must be updated in step.

This document is authoritative for traceability purposes. Any discrepancy between this RTM and the underlying spec documents should be resolved by updating the spec document and then regenerating the affected RTM entries.

---

## 2. Requirements Summary

### PRD Features (F0–F4) — all P0 / MVP

- **F0: File Upload Interface** — Browser-based PDF file picker and drag-and-drop drop zone; client-side type and size validation; upload progress indicator; keyboard accessibility.
- **F1: Server-Side PDF-to-DOCX Conversion** — Server-side file validation (magic bytes, MIME, size); UUID-based temp file creation; conversion via `pdf2docx` with LibreOffice headless fallback; 60-second timeout; image-only PDF detection.
- **F2: DOCX File Download** — Streaming download delivery; derived filename mapping (`*.pdf` → `*.docx`); `Content-Disposition: attachment`; post-download temp file deletion; single-download enforcement.
- **F3: User Feedback & Status Communication** — UI state machine (`IDLE → UPLOADING → CONVERTING → SUCCESS / ERROR`); real-time progress bar; spinner; success and error states; mapped error messages; retry without page reload; ARIA accessibility.
- **F4: File Security & Privacy Controls** — Server-side MIME magic-byte inspection; hard 50 MB size cap; UUID-only on-disk filenames; `600`/`700` file permissions; immediate post-download deletion; TTL background sweep (60-minute default, 10-minute interval); concurrent job limit (default 5); no content logging.

### FRD Functional Requirements (F00–F04)

- **F00** defines the browser upload UI contract: file picker, drag-and-drop, client-side validation, progress indicator, and keyboard navigation.
- **F01** defines the server-side conversion contract: magic-byte validation, size enforcement, UUID temp file creation, `pdf2docx` + LibreOffice pipeline, 60-second timeout, image-only detection, and structured JSON responses.
- **F02** defines the download delivery contract: `GET /api/download/{job_id}`, streaming response, derived filename, post-download cleanup, single-use enforcement.
- **F03** defines the UI state machine contract: five states (`IDLE`, `UPLOADING`, `CONVERTING`, `SUCCESS`, `ERROR`), valid transitions, error message map, ARIA live regions.
- **F04** defines the security and privacy contract: MIME inspection, size enforcement, UUID naming, permissions, immediate and TTL cleanup, no content logging, concurrent job limit.

### TechArch Specifications

- **API Layer** — `POST /api/convert` and `GET /api/download/{job_id}` endpoints; `GET /api/health`; error catalog with ten machine-readable error codes.
- **Validation Service** (`services/validation.py`) — Magic-byte check, MIME check, byte-count enforcement.
- **Conversion Service** (`services/conversion.py`) — UUID generation, temp dir creation, `pdf2docx` invocation, LibreOffice fallback subprocess, timeout watchdog, image-only detection, job registry updates.
- **Download Service** (`services/download.py`) — Job registry lookup, streaming `StreamingResponse`, post-send cleanup callback.
- **Job Registry** (`core/registry.py`) — Thread-safe in-memory `dict[str, JobRecord]`; states `PENDING`, `CONVERTING`, `COMPLETED`, `DOWNLOADED`, `FAILED`.
- **TTL Sweep** (`core/cleanup.py`) — Periodic `asyncio` task every `SWEEP_INTERVAL_MINUTES`; deletes dirs older than `TTL_MINUTES`.
- **Frontend State Machine** (`app.js`) — `setState()` managing `IDLE → UPLOADING → CONVERTING → SUCCESS / ERROR`; `XMLHttpRequest` upload progress; error message map.
- **Security Controls** — UUID-only on-disk filenames, `600`/`700` permissions, `shell=False` subprocess, `Cache-Control: no-store`, CSP meta tag.
- **Configuration** (`core/config.py`) — Eight environment variables: `TEMP_DIR`, `MAX_FILE_SIZE_BYTES`, `JOB_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, `TTL_MINUTES`, `SWEEP_INTERVAL_MINUTES`, `ALLOWED_ORIGINS`, `LOG_LEVEL`.

### User Stories

- **27 stories** across 5 epics (US-0.1–US-0.6, US-1.1–US-1.5, US-2.1–US-2.4, US-3.1–US-3.6, US-4.1–US-4.6).
- All stories are priority **P0** (Critical / MVP).
- Personas: Marcus Webb (office professional), Priya Nair (student/academic), Dana Okafor (freelancer/SMB owner).

---

## 3. Traceability Matrix

### 3.1 Primary Traceability: PRD Feature → FRD Section → TechArch Component → User Stories

| PRD Feature | FRD Section | TechArch Component | User Stories |
|---|---|---|---|
| **F0: File Upload Interface** | F00: File Upload Interface | Frontend `app.js` state machine; `index.html` drop zone & file input; client-side validation | US-0.1, US-0.2, US-0.3, US-0.4, US-0.5, US-0.6 |
| **F1: Server-Side PDF-to-DOCX Conversion** | F01: Server-Side PDF-to-DOCX Conversion | `routers/convert.py`; `services/validation.py`; `services/conversion.py`; `core/registry.py`; pdf2docx integration; LibreOffice fallback subprocess | US-1.1, US-1.2, US-1.3, US-1.4, US-1.5 |
| **F2: DOCX File Download** | F02: DOCX File Download | `routers/download.py`; `services/download.py`; `StreamingResponse`; post-send cleanup callback | US-2.1, US-2.2, US-2.3, US-2.4 |
| **F3: User Feedback & Status Communication** | F03: User Feedback & Status Communication | Frontend `app.js` state machine (`IDLE→UPLOADING→CONVERTING→SUCCESS/ERROR`); ARIA live regions; error message map | US-3.1, US-3.2, US-3.3, US-3.4, US-3.5, US-3.6 |
| **F4: File Security & Privacy Controls** | F04: File Security & Privacy Controls | `services/validation.py` (magic bytes); `services/conversion.py` (UUID naming, permissions); `core/cleanup.py` (TTL sweep); `core/registry.py` (concurrent job limit); `core/config.py` (env vars) | US-4.1, US-4.2, US-4.3, US-4.4, US-4.5, US-4.6 |

---

### 3.2 API Endpoint Traceability

| API Endpoint | PRD Feature | FRD Section | TechArch Router | User Stories |
|---|---|---|---|---|
| `POST /api/convert` | F0, F1, F4 | F00, F01, F04 | `routers/convert.py` | US-0.5, US-1.1–US-1.5, US-4.1, US-4.2, US-4.5 |
| `GET /api/download/{job_id}` | F2, F3 | F02, F03 | `routers/download.py` | US-2.1–US-2.4, US-3.3 |
| `GET /api/health` | F1, F4 | F01 (operational) | `main.py` | US-4.5 (concurrent job monitoring) |

---

### 3.3 Error Code Traceability

| Error Code | HTTP Status | PRD Feature | FRD Section | User Story |
|---|---|---|---|---|
| `INVALID_FILE_TYPE` | 400 | F0, F1, F4 | F00, F01, F04 | US-0.3, US-1.5, US-4.1 |
| `FILE_TOO_LARGE` | 413 | F0, F1, F4 | F00, F01, F04 | US-0.4, US-1.5, US-4.1 |
| `CONVERSION_TIMEOUT` | 504 | F1, F3 | F01, F03 | US-1.3, US-3.4 |
| `CONVERSION_FAILED` | 422 | F1, F3 | F01, F03 | US-1.2, US-3.4 |
| `IMAGE_ONLY_PDF` | 422 | F1, F3 | F01, F03 | US-1.4, US-3.4 |
| `SERVER_BUSY` | 503 | F1, F3, F4 | F01, F03, F04 | US-4.5, US-3.4 |
| `INTERNAL_ERROR` | 500 | F1, F2 | F01, F02 | US-3.4 |
| `JOB_NOT_FOUND` | 404 | F2, F3 | F02, F03 | US-2.3, US-2.4, US-3.3 |
| `JOB_FAILED` | 410 | F2, F3 | F02, F03 | US-2.4, US-3.4 |
| `INVALID_JOB_ID` | 400 | F2 | F02 | US-2.4 |

---

### 3.4 Security Control Traceability

| Security Control | PRD Feature | FRD Section | TechArch Mechanism | User Story |
|---|---|---|---|---|
| Magic byte validation (`%PDF`) | F1, F4 | F01, F04 | `services/validation.py` — first 8 bytes check | US-1.5, US-4.1 |
| MIME type check (`application/pdf`) | F0, F1, F4 | F00, F01, F04 | Client: `file.type`; Server: `Content-Type` header | US-0.3, US-1.5, US-4.1 |
| Hard file size cap (50 MB) | F0, F1, F4 | F00, F01, F04 | Client: `file.size`; Server: byte counter in `validation.py` | US-0.4, US-1.5, US-4.1 |
| UUID v4 on-disk filenames | F4 | F04 | `services/conversion.py` — `uuid.uuid4()` | US-4.2 |
| File permissions `600` / dir `700` | F4 | F04 | `services/conversion.py` — `os.makedirs`, `open()` | US-4.2 |
| `shell=False` subprocess | F1, F4 | F01, F04 | `services/conversion.py` — LibreOffice `subprocess.run` | US-4.2 |
| Post-download immediate deletion | F2, F4 | F02, F04 | `services/download.py` — post-send callback | US-2.3, US-4.3 |
| TTL background sweep | F4 | F04 | `core/cleanup.py` — `asyncio` periodic task | US-4.4 |
| Concurrent job limit | F1, F4 | F01, F04 | `core/registry.py` — atomic counter | US-4.5 |
| No content logging | F4 | F04 | Application logging policy — `job_id` + outcome only | US-4.6 |
| `Cache-Control: no-store` | F2, F4 | F02 | `routers/download.py` response headers | US-2.3 |
| Content Security Policy | F4 | F04 | `index.html` — CSP meta tag | US-4.6 |

---

## 4. Requirements Detail

### F0: File Upload Interface

**PRD Capability:** Single PDF file upload via picker or drag-and-drop; client-side validation (type, size); progress indicator; CTA button; keyboard accessibility.

**FRD Functional Requirements (F00):**
- MUST accept only files with MIME type `application/pdf` and `.pdf` extension (client check)
- MUST reject files exceeding 52,428,800 bytes before upload begins
- MUST disable "Convert to DOCX" button until a valid file is selected
- MUST prevent default browser drag-over behaviour on drag events
- MUST display human-readable file size alongside filename after selection
- MUST be fully keyboard navigable (`Enter`/`Space` on file picker; `Enter` on Convert button)
- SHOULD support drag-and-drop with the same validation as file picker
- MUST reset validation state and re-run checks on file change

**TechArch Implementation References:**
- `index.html`: `<input type="file" accept=".pdf,application/pdf">`, drop zone `<div>`, `<progress>` element, `aria-live="polite"` status banner
- `app.js`: `setState()` transitions, `file.type`/`file.name`/`file.size` client-side checks, `XMLHttpRequest` + `upload.onprogress`, keyboard event handlers (`Enter`/`Space`)

**Linked User Stories:**
- US-0.1: Select a PDF via File Picker
- US-0.2: Upload PDF via Drag-and-Drop
- US-0.3: Client-Side File Type Validation
- US-0.4: Client-Side File Size Guard
- US-0.5: Upload Progress Indicator
- US-0.6: Keyboard-Accessible Upload Interface

---

### F1: Server-Side PDF-to-DOCX Conversion

**PRD Capability:** Server-side file validation; secure temp file write; `pdf2docx` conversion with LibreOffice fallback; 60-second timeout; return `job_id` on success.

**FRD Functional Requirements (F01):**
- MUST validate MIME type server-side using magic bytes (`%PDF`) regardless of declared `Content-Type`
- MUST reject any file exceeding 52,428,800 bytes
- MUST assign UUID v4 `job_id` to every accepted job before writing to disk
- MUST write source file to `{TEMP_DIR}/{job_id}/{job_id}.pdf` with permissions `600`
- MUST enforce a 60-second hard timeout on the conversion process
- MUST attempt LibreOffice headless fallback if `pdf2docx` raises an exception
- MUST detect image-only PDFs (zero non-whitespace text paragraphs in output DOCX) and return `IMAGE_ONLY_PDF`
- MUST delete all temp files for a job on any conversion failure before returning error response
- MUST NOT execute or interpret uploaded file content other than passing path to conversion library
- MUST NOT use original filename when writing to disk
- SHOULD log conversion duration and outcome without logging file content or user metadata

**TechArch Implementation References:**
- `routers/convert.py`: `POST /api/convert` endpoint; delegates to `ValidationService` and `ConversionService`
- `services/validation.py`: reads first 8 bytes; checks `25 50 44 46` (`%PDF`); counts bytes; rejects on limit exceeded
- `services/conversion.py`: `uuid.uuid4()` job ID; `os.makedirs(..., mode=0o700)`; `open(..., mode=0o600)`; `pdf2docx.Converter.convert()`; `concurrent.futures.ThreadPoolExecutor` with `JOB_TIMEOUT_SECONDS` deadline; `subprocess.run(["libreoffice", "--headless", ...], shell=False)`; `python-docx` paragraph text inspection for image-only detection
- `core/registry.py`: registers job as `CONVERTING`; updates to `COMPLETED` or `FAILED`

**Linked User Stories:**
- US-1.1: Convert a Text-Based PDF to DOCX
- US-1.2: Fallback Conversion via LibreOffice
- US-1.3: Conversion Timeout Enforcement
- US-1.4: Image-Only PDF Detection
- US-1.5: Server-Side File Validation Before Conversion

---

### F2: DOCX File Download

**PRD Capability:** Serve converted DOCX as HTTP download with derived filename; post-download temp file deletion; single-use enforcement.

**FRD Functional Requirements (F02):**
- MUST validate `job_id` format (UUID v4 regex) before any file system access
- MUST return `404 JOB_NOT_FOUND` for any `job_id` not present in job registry
- MUST set `Content-Disposition: attachment` (never `inline`) to force browser download
- MUST set `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- MUST derive download filename from original PDF filename (not from on-disk `job_id` filename)
- MUST sanitise derived filename: strip `/`, `\`, null bytes; limit to 255 characters
- MUST delete both `.pdf` and `.docx` temp files after response body is sent
- MUST use streaming (chunked) file delivery — do not load entire DOCX into memory
- MUST NOT allow a `job_id` to be downloaded more than once (repeat request returns `404`)
- SHOULD set `Cache-Control: no-store` on download response

**TechArch Implementation References:**
- `routers/download.py`: `GET /api/download/{job_id}`; UUID v4 regex validation; delegates to `DownloadService`
- `services/download.py`: `JobRegistry` lookup; `StreamingResponse` with 64 KB chunk size; `Content-Disposition`, `Content-Type`, `Content-Length`, `Cache-Control: no-store` headers; post-send `shutil.rmtree()` callback; registry update to `DOWNLOADED`

**Linked User Stories:**
- US-2.1: Automatic DOCX Download After Conversion
- US-2.2: Meaningful Download Filename
- US-2.3: Post-Download Temp File Cleanup
- US-2.4: Handle Expired or Unknown Download Links

---

### F3: User Feedback & Status Communication

**PRD Capability:** UI state machine with five states; real-time progress bar; "Converting…" spinner; success state; mapped error messages; retry without page reload; screen reader accessibility.

**FRD Functional Requirements (F03):**
- MUST implement five mutually exclusive UI states: `IDLE`, `UPLOADING`, `CONVERTING`, `SUCCESS`, `ERROR`
- MUST enforce only the valid state transitions listed in the state transition table
- MUST map every defined server error code to a user-friendly message (Error Message Map)
- MUST display generic fallback message for any unmapped error code
- MUST reset file input field when user clicks "Try Again"
- MUST transition from `SUCCESS` to `ERROR` if `GET /api/download/{job_id}` returns non-200
- MUST NOT display raw error codes, stack traces, or internal server details to the user
- MUST ensure "Try Again" button is keyboard-focusable and activatable
- SHOULD colour-code states (neutral/blue for progress, green for success, red for error)
- SHOULD announce state transitions via `aria-live="polite"` ARIA live regions

**TechArch Implementation References:**
- `app.js`: `setState(newState)` function; `IDLE → UPLOADING → CONVERTING → SUCCESS / ERROR → IDLE` transitions; `xhr.upload.onprogress` handler; Error Message Map (10 error code mappings); `<a download>` anchor for download trigger
- `index.html`: `<progress>` element; status banner `<div aria-live="polite">`; error detail `<p>`; "Try Again" `<button>`; "Convert Another File" `<a>`

**Linked User Stories:**
- US-3.1: Upload Progress Feedback
- US-3.2: Conversion-in-Progress Status Indicator
- US-3.3: Conversion Success State
- US-3.4: Actionable Error Messages
- US-3.5: Retry Without Page Reload
- US-3.6: Screen Reader Accessibility for State Changes

---

### F4: File Security & Privacy Controls

**PRD Capability:** Server-side MIME inspection; configurable size cap; UUID-only temp filenames; `600`/`700` permissions; immediate post-download deletion; TTL sweep; concurrent job limit; no content logging.

**FRD Functional Requirements (F04):**
- MUST inspect magic bytes server-side for every upload regardless of declared MIME type
- MUST reject files whose first 4 bytes are not `25 50 44 46` (`%PDF`)
- MUST enforce 50 MB limit server-side regardless of client-side validation
- MUST use UUID v4 as on-disk filename for all temp files (never original filename)
- MUST set temp file permissions to `600` and temp directory permissions to `700`
- MUST delete temp files immediately on any conversion failure
- MUST delete temp files after successful download delivery
- MUST run TTL sweep to delete orphaned files older than 60 minutes (default)
- MUST limit concurrent active conversion jobs (default: 5)
- MUST NOT log file content, original filename, or any user-identifying metadata
- MUST NOT pass original filename to any shell command
- MUST NOT execute uploaded file content; only pass file path to conversion library
- SHOULD store `TEMP_DIR`, `MAX_FILE_SIZE_BYTES`, `JOB_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, `TTL_MINUTES` as configurable environment variables
- MUST NOT serve any temp file via a guessable or sequential URL

**TechArch Implementation References:**
- `services/validation.py`: magic byte check; MIME check; byte counter
- `services/conversion.py`: `uuid.uuid4()`; `os.makedirs(mode=0o700)`; `open(mode=0o600)`; `shell=False` in all subprocess calls; original filename never used in any `os.path` operation
- `core/cleanup.py`: `asyncio` periodic task; `os.scandir(TEMP_DIR)`; `os.stat()` age check; `shutil.rmtree()` on expired dirs; log count + bytes freed only
- `core/registry.py`: atomic counter for concurrent job enforcement; `503 SERVER_BUSY` on limit
- `core/config.py`: `pydantic-settings` — `TEMP_DIR`, `MAX_FILE_SIZE_BYTES`, `JOB_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, `TTL_MINUTES`, `SWEEP_INTERVAL_MINUTES`, `ALLOWED_ORIGINS`, `LOG_LEVEL`
- `index.html`: CSP meta tag restricting all resource loading to same origin

**Linked User Stories:**
- US-4.1: Server-Side MIME Validation Regardless of Client Claims
- US-4.2: UUID-Based Temp File Naming to Prevent Path Traversal
- US-4.3: Immediate Temp File Deletion After Download
- US-4.4: TTL Background Sweep for Orphaned Files
- US-4.5: Concurrent Job Limit to Prevent Resource Exhaustion
- US-4.6: No Logging of File Content or User-Identifying Metadata

---

## 5. Test Case Coverage

### 5.1 Test Case Registry

| Test ID | Test Case Description | PRD Feature | FRD Section | User Story | Type | Expected Result |
|---|---|---|---|---|---|---|
| TEST-001 | Select valid PDF via file picker — verify filename and size displayed, Convert button enabled | F0 | F00 | US-0.1 | UI / Functional | Filename + size shown; button enabled |
| TEST-002 | Select non-PDF file via file picker — verify inline error and button disabled | F0 | F00 | US-0.3 | UI / Validation | Error "Please select a PDF file." shown; button disabled |
| TEST-003 | Select file > 50 MB — verify inline error before upload starts | F0 | F00 | US-0.4 | UI / Validation | Error "File too large. Maximum size is 50 MB." shown; button disabled |
| TEST-004 | Drag valid PDF onto drop zone — verify same validation as file picker | F0 | F00 | US-0.2 | UI / Functional | File accepted; filename shown; button enabled |
| TEST-005 | Drag non-PDF onto drop zone — verify inline error | F0 | F00 | US-0.2, US-0.3 | UI / Validation | Error "Please select a PDF file." shown |
| TEST-006 | Drag file over drop zone — verify browser default prevented and hover state shown | F0 | F00 | US-0.2 | UI / Functional | Default dragover prevented; highlight state applied |
| TEST-007 | Upload progress bar updates from 0–100% during file transmission | F0 | F00 | US-0.5 | UI / Functional | Progress element value increments continuously |
| TEST-008 | Convert button disabled with spinner during upload | F0 | F00 | US-0.5 | UI / Functional | Button disabled; spinner visible |
| TEST-009 | Keyboard: file picker activatable via Enter/Space; Convert button activatable via Enter | F0 | F00 | US-0.6 | Accessibility | All actions complete without mouse |
| TEST-010 | Tab order is logical across all interactive elements | F0 | F00 | US-0.6 | Accessibility | Tab moves through elements in expected order |
| TEST-011 | POST /api/convert with valid text-based PDF — verify 200 OK with job_id, filename, file_size_bytes | F1 | F01 | US-1.1 | API / Functional | `{"job_id": "<uuid>", "filename": "*.docx", "file_size_bytes": N}` |
| TEST-012 | Output DOCX is non-empty, openable, and contains paragraphs from source PDF | F1 | F01 | US-1.1 | Integration | DOCX file present on disk; contains text paragraphs |
| TEST-013 | POST /api/convert with file whose first bytes are not `%PDF` — verify 400 INVALID_FILE_TYPE, no file written to disk | F1, F4 | F01, F04 | US-1.5, US-4.1 | API / Security | `400` + `INVALID_FILE_TYPE`; no file in TEMP_DIR |
| TEST-014 | POST /api/convert with file > 50 MB — verify 413 FILE_TOO_LARGE | F1, F4 | F01, F04 | US-1.5, US-4.1 | API / Validation | `413` + `FILE_TOO_LARGE` |
| TEST-015 | `pdf2docx` raises exception — verify LibreOffice fallback is invoked automatically | F1 | F01 | US-1.2 | Integration | Fallback invoked; conversion succeeds if LibreOffice available |
| TEST-016 | Both `pdf2docx` and LibreOffice fail — verify 422 CONVERSION_FAILED | F1 | F01 | US-1.2 | API / Error | `422` + `CONVERSION_FAILED`; temp files deleted |
| TEST-017 | Conversion exceeds 60-second timeout — verify 504 CONVERSION_TIMEOUT and temp file deletion | F1 | F01 | US-1.3 | API / Error | `504` + `CONVERSION_TIMEOUT`; no files in job dir |
| TEST-018 | Image-only (scanned) PDF — verify 422 IMAGE_ONLY_PDF and no DOCX served | F1 | F01 | US-1.4 | API / Functional | `422` + `IMAGE_ONLY_PDF`; empty DOCX not returned |
| TEST-019 | Temp file created with UUID-based path; original filename not present on disk | F1, F4 | F01, F04 | US-4.2 | Security | `TEMP_DIR/{uuid}/{uuid}.pdf` exists; original name absent |
| TEST-020 | Temp file permissions are `600`; directory permissions are `700` | F4 | F04 | US-4.2 | Security | `stat` confirms `0o600` / `0o700` |
| TEST-021 | GET /api/download/{job_id} — verify 200 OK with binary DOCX body, correct headers | F2 | F02 | US-2.1 | API / Functional | Binary body; `Content-Disposition: attachment`; correct `Content-Type` |
| TEST-022 | Download filename derived from original PDF filename (e.g., report.pdf → report.docx) | F2 | F02 | US-2.2 | API / Functional | `Content-Disposition` filename matches derived name |
| TEST-023 | Derived filename sanitised: no `/`, `\`, null bytes; max 255 chars | F2 | F02 | US-2.2 | Security | Sanitised filename in headers |
| TEST-024 | Both .pdf and .docx temp files deleted from server after download completes | F2, F4 | F02, F04 | US-2.3, US-4.3 | Integration | Job directory absent from `TEMP_DIR` after response |
| TEST-025 | Second GET /api/download/{job_id} after cleanup returns 404 JOB_NOT_FOUND | F2 | F02 | US-2.3 | API / Functional | `404` + `JOB_NOT_FOUND` |
| TEST-026 | Cache-Control: no-store present on download response | F2, F4 | F02 | US-2.3 | API / Security | Response header `Cache-Control: no-store` confirmed |
| TEST-027 | GET /api/download/{job_id} for unknown job_id returns 404 JOB_NOT_FOUND | F2 | F02 | US-2.4 | API / Error | `404` + `JOB_NOT_FOUND` |
| TEST-028 | GET /api/download/{job_id} with invalid UUID format returns 400 INVALID_JOB_ID | F2 | F02 | US-2.4 | API / Validation | `400` + `INVALID_JOB_ID` |
| TEST-029 | GET /api/download/{job_id} for failed job returns 410 JOB_FAILED | F2 | F02 | US-2.4 | API / Error | `410` + `JOB_FAILED` |
| TEST-030 | UI transitions IDLE → UPLOADING on Convert click; progress bar visible | F3 | F03 | US-3.1 | UI / Functional | State = `UPLOADING`; progress bar visible |
| TEST-031 | UI transitions UPLOADING → CONVERTING when upload reaches 100% | F3 | F03 | US-3.2 | UI / Functional | State = `CONVERTING`; spinner shown; progress bar hidden |
| TEST-032 | UI transitions CONVERTING → SUCCESS on 200 from server; green tick + "Your DOCX is ready!" shown | F3 | F03 | US-3.3 | UI / Functional | State = `SUCCESS`; success message and Download button visible |
| TEST-033 | Upload network error transitions UI to ERROR with "Upload failed" message | F3 | F03 | US-3.1 | UI / Error | State = `ERROR`; "Upload failed. Please check your connection and try again." |
| TEST-034 | Each of the 10 server error codes maps to correct user-facing message in ERROR state | F3 | F03 | US-3.4 | UI / Error | All 10 error codes produce correct mapped messages |
| TEST-035 | Raw error codes and stack traces never displayed to user | F3 | F03 | US-3.4 | UI / Security | No `error_code` or stack trace in DOM |
| TEST-036 | "Try Again" button resets UI to IDLE; file input cleared; error cleared | F3 | F03 | US-3.5 | UI / Functional | State = `IDLE`; file input value empty; error banner hidden |
| TEST-037 | "Try Again" button keyboard-focusable and activatable via Enter | F3 | F03 | US-3.5 | Accessibility | Button responds to keyboard Enter in ERROR state |
| TEST-038 | ARIA live region announces state transitions to screen readers | F3 | F03 | US-3.6 | Accessibility | `aria-live="polite"` region content updates on each state change |
| TEST-039 | Success and error icons have accessible text alternatives (aria-label / alt) | F3 | F03 | US-3.6 | Accessibility | Icons have non-empty accessible names |
| TEST-040 | Server-side magic byte check is independent of Content-Type header | F4 | F04 | US-4.1 | Security | File with spoofed `application/pdf` MIME but non-PDF bytes returns `400 INVALID_FILE_TYPE` |
| TEST-041 | Server-side 50 MB size limit enforced regardless of client-side check | F4 | F04 | US-4.1 | Security | Direct API POST with >50 MB body returns `413 FILE_TOO_LARGE` |
| TEST-042 | Original filename never used in os.path operations (path traversal prevention) | F4 | F04 | US-4.2 | Security | Filename `../../etc/passwd.pdf` does not cause path traversal |
| TEST-043 | LibreOffice subprocess invoked with shell=False | F4 | F04 | US-4.2 | Security | Code review / unit test confirms `shell=False` |
| TEST-044 | Temp files for failed job deleted before error response returned | F4 | F04 | US-4.3 | Integration | Job dir absent after 422/504 response |
| TEST-045 | TTL sweep deletes job dirs older than 60 minutes | F4 | F04 | US-4.4 | Integration | Manually created stale dir removed after sweep |
| TEST-046 | TTL sweep logs only count and bytes freed — no file content or filenames | F4 | F04 | US-4.4 | Security | Log output contains no filenames or document metadata |
| TEST-047 | TTL and sweep interval configurable via TTL_MINUTES and SWEEP_INTERVAL_MINUTES env vars | F4 | F04 | US-4.4 | Configuration | Custom TTL value honoured by sweep logic |
| TEST-048 | Concurrent job limit enforced: 6th simultaneous job returns 503 SERVER_BUSY | F4 | F04 | US-4.5 | Load / Functional | `503` + `SERVER_BUSY` when 5 jobs already active |
| TEST-049 | Job counter decremented on job completion (success, failure, and timeout) | F4 | F04 | US-4.5 | Integration | Slot available again after previous job completes |
| TEST-050 | Server logs contain no file content, original filenames, or user metadata | F4 | F04 | US-4.6 | Security | Log lines contain only `job_id`, `duration_ms`, `outcome`, `file_size_bytes` |

---

### 5.2 Coverage Matrix by Feature

| PRD Feature | User Stories | Test Cases | Tests per Story (avg) | Coverage |
|---|---|---|---|---|
| F0: File Upload Interface | US-0.1–US-0.6 (6 stories) | TEST-001–TEST-010 (10 tests) | 1.7 | 100% |
| F1: Server-Side PDF-to-DOCX Conversion | US-1.1–US-1.5 (5 stories) | TEST-011–TEST-020 (10 tests) | 2.0 | 100% |
| F2: DOCX File Download | US-2.1–US-2.4 (4 stories) | TEST-021–TEST-029 (9 tests) | 2.3 | 100% |
| F3: User Feedback & Status Communication | US-3.1–US-3.6 (6 stories) | TEST-030–TEST-039 (10 tests) | 1.7 | 100% |
| F4: File Security & Privacy Controls | US-4.1–US-4.6 (6 stories) | TEST-040–TEST-050 (11 tests) | 1.8 | 100% |
| **Totals** | **27 stories** | **50 test cases** | **1.9 avg** | **100%** |

---

### 5.3 Test Type Distribution

| Test Type | Count | % of Total |
|---|---|---|
| UI / Functional | 15 | 30% |
| API / Functional | 9 | 18% |
| Security | 10 | 20% |
| Integration | 8 | 16% |
| Accessibility | 5 | 10% |
| API / Validation | 3 | 6% |
| **Total** | **50** | **100%** |

---

### 5.4 Story-to-Test Mapping

| Story ID | Story Title | Test IDs |
|---|---|---|
| US-0.1 | Select a PDF via File Picker | TEST-001, TEST-002 |
| US-0.2 | Upload PDF via Drag-and-Drop | TEST-004, TEST-005, TEST-006 |
| US-0.3 | Client-Side File Type Validation | TEST-002, TEST-005 |
| US-0.4 | Client-Side File Size Guard | TEST-003 |
| US-0.5 | Upload Progress Indicator | TEST-007, TEST-008 |
| US-0.6 | Keyboard-Accessible Upload Interface | TEST-009, TEST-010 |
| US-1.1 | Convert a Text-Based PDF to DOCX | TEST-011, TEST-012 |
| US-1.2 | Fallback Conversion via LibreOffice | TEST-015, TEST-016 |
| US-1.3 | Conversion Timeout Enforcement | TEST-017 |
| US-1.4 | Image-Only PDF Detection | TEST-018 |
| US-1.5 | Server-Side File Validation Before Conversion | TEST-013, TEST-014 |
| US-2.1 | Automatic DOCX Download After Conversion | TEST-021 |
| US-2.2 | Meaningful Download Filename | TEST-022, TEST-023 |
| US-2.3 | Post-Download Temp File Cleanup | TEST-024, TEST-025, TEST-026 |
| US-2.4 | Handle Expired or Unknown Download Links | TEST-027, TEST-028, TEST-029 |
| US-3.1 | Upload Progress Feedback | TEST-030, TEST-033 |
| US-3.2 | Conversion-in-Progress Status Indicator | TEST-031 |
| US-3.3 | Conversion Success State | TEST-032 |
| US-3.4 | Actionable Error Messages | TEST-034, TEST-035 |
| US-3.5 | Retry Without Page Reload | TEST-036, TEST-037 |
| US-3.6 | Screen Reader Accessibility for State Changes | TEST-038, TEST-039 |
| US-4.1 | Server-Side MIME Validation Regardless of Client Claims | TEST-040, TEST-041 |
| US-4.2 | UUID-Based Temp File Naming to Prevent Path Traversal | TEST-042, TEST-043 |
| US-4.3 | Immediate Temp File Deletion After Download | TEST-044 |
| US-4.4 | TTL Background Sweep for Orphaned Files | TEST-045, TEST-046, TEST-047 |
| US-4.5 | Concurrent Job Limit to Prevent Resource Exhaustion | TEST-048, TEST-049 |
| US-4.6 | No Logging of File Content or User-Identifying Metadata | TEST-050 |

---

## 6. Change Management

### 6.1 Change Log

| Change ID | Date | Version | Changed By | Section(s) Affected | Description | Impact |
|---|---|---|---|---|---|---|
| CHG-001 | 2026-05-12 | 1.0 | Spec Generator | All | Initial RTM created from PRD v1.0, FRD v1.0, TechArch v1.0, UserStories v1.0 | Baseline established |

---

### 6.2 Change Impact Assessment Procedure

When any upstream specification document changes, the following impact assessment must be performed before updating the RTM:

1. **PRD change** (new/modified feature) → Update Section 3.1 Primary Traceability; add/modify FRD sections, TechArch components, and User Stories in Section 4; add/modify test cases in Section 5.
2. **FRD change** (new/modified requirement) → Verify PRD feature still covers the requirement (Section 3.1); update Requirements Detail (Section 4); check if new test cases are required (Section 5).
3. **TechArch change** (new/modified component or API) → Update Section 3.1 and Section 3.2 (API endpoints); update implementation references in Section 4; verify test cases still reference correct components (Section 5).
4. **UserStories change** (new/modified story) → Update Section 3.1 User Stories column; update linked stories in Section 4; update Sections 5.2–5.4 (coverage matrix and story-to-test mapping).
5. **Test case addition/removal** → Update Section 5.1 registry; recalculate Section 5.2 coverage matrix; update Section 5.4 story-to-test mapping.

All changes must be logged in Section 6.1 with a `CHG-NNN` identifier before the RTM is re-issued.

---

## 7. Approval

### 7.1 Document Sign-Off

| Role | Name | Signature | Date | Status |
|---|---|---|---|---|
| Product Owner | — | _______________________ | ____________ | Pending |
| Engineering Lead | — | _______________________ | ____________ | Pending |
| QA Lead | — | _______________________ | ____________ | Pending |
| Security Reviewer | — | _______________________ | ____________ | Pending |

---

### 7.2 Traceability Completeness Checklist

Before sign-off, the approving parties confirm:

- [x] All 5 PRD features (F0–F4) have at least one FRD section entry in the traceability matrix
- [x] All 5 FRD sections (F00–F04) map back to a PRD feature
- [x] All 5 FRD sections have at least one TechArch component reference
- [x] All 5 PRD features have at least one User Story
- [x] All 27 User Stories are linked to at least one test case
- [x] All 50 test cases are linked to at least one User Story
- [x] All 10 API error codes are traced to a PRD feature and User Story
- [x] All 12 security controls are traced to a PRD feature and User Story
- [x] Coverage is 100% across all 5 features
- [ ] All test cases have been executed and results recorded *(pending implementation)*
- [ ] All approvers have signed Section 7.1 *(pending review cycle)*

---

*Document generated: 2026-05-12 | Project: PDFConverter | Version: 1.0*
*Sources: PRD-PDFConverter.md v1.0 · FRD-PDFConverter.md v1.0 · TechArch-PDFConverter.md v1.0 · UserStories-PDFConverter.md v1.0*
