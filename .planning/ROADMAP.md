# Roadmap: PDF to DOCX Converter

## Overview

Five phases deliver the complete MVP: first the server foundation is scaffolded, then the upload UI is built, then the conversion engine is wired up, then download and privacy cleanup are completed, and finally the full feedback state machine is polished. Each phase delivers a verifiable capability. After Phase 5 completes, a user can upload any PDF, receive a faithful DOCX conversion, and download it — with clear feedback at every step and no trace of their file left on the server.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Project scaffolding, FastAPI server skeleton, configuration, and static file serving
- [ ] **Phase 2: Upload Interface** - Browser upload UI with drag-and-drop, file picker, client-side validation, and progress indicator
- [ ] **Phase 3: Conversion Engine** - Server-side PDF-to-DOCX conversion with timeout, fallback, image-only detection, and input validation
- [ ] **Phase 4: Download & Cleanup** - DOCX file delivery, derived filename, post-download deletion, and TTL orphan sweep
- [ ] **Phase 5: Feedback & Polish** - Full UI state machine, specific error messages, retry flow, and privacy statement

## Phase Details

### Phase 1: Foundation
**Status**: passed
**Goal**: A running server that serves the frontend and is ready to receive upload requests
**Depends on**: Nothing (first phase)
**Requirements**: *(infrastructure — enables all other phases; no direct requirement IDs)*
**Success Criteria** (what must be TRUE):
  1. `uvicorn` starts without errors and serves `index.html` at `/`
  2. `GET /api/health` returns `{ "status": "ok" }` with 200
  3. Environment variables (`TEMP_DIR`, `MAX_FILE_SIZE_BYTES`, `JOB_TIMEOUT_SECONDS`, `MAX_CONCURRENT_JOBS`, `TTL_MINUTES`) load from `.env` with typed defaults
  4. Temp directory (`/tmp/pdfconverter/`) is created on startup and is writable
**Plans**: 2 plans

Plans:
- [ ] 01-01-PLAN.md — Project scaffold: directory layout, requirements.txt, core/config.py, models/schemas.py, core/registry.py
- [ ] 01-02-PLAN.md — App wiring: main.py (FastAPI app, CORS, health endpoint, static serving, lifecycle hooks), placeholder static files

### Phase 2: Upload Interface
**Status**: executing
**Goal**: Users can select a PDF (via file picker or drag-and-drop) and see client-side validation before any server request is made
**Depends on**: Phase 1
**Requirements**: UPLD-01, UPLD-02, UPLD-03, UPLD-04, UPLD-05
**Success Criteria** (what must be TRUE):
  1. User can drag a PDF file onto the drop zone and see its name and size displayed
  2. User can click the file picker button and select a PDF from their filesystem
  3. User sees an inline error immediately (without a server round-trip) if they select a non-PDF file
  4. User sees an inline error immediately if they select a file larger than 50 MB
  5. User sees a progress bar filling from 0% to 100% while the file uploads to the server
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — index.html + styles.css + playwright.config.ts: full semantic markup (all TechArch §2.2 elements), responsive CSS state classes, Playwright test runner setup
- [ ] 02-02-PLAN.md — app.js + e2e/upload-interface.spec.ts: state machine (IDLE/UPLOADING/CONVERTING/SUCCESS/ERROR), drag-drop, type/size validation, XHR upload with progress, keyboard accessibility, Playwright e2e tests

### Phase 3: Conversion Engine
**Goal**: The server accepts a valid PDF upload, converts it to DOCX, and returns a job ID — rejecting invalid files and timed-out jobs with structured errors
**Depends on**: Phase 2
**Requirements**: CONV-01, CONV-02, CONV-03, SECU-01, SECU-04
**Success Criteria** (what must be TRUE):
  1. A valid text-based PDF uploaded via `POST /api/convert` produces a `200 OK` response with `job_id` and `filename`
  2. A file whose bytes are not a valid PDF (fails magic byte check) is rejected with `400 INVALID_FILE_TYPE` — no file is written to disk
  3. A conversion that exceeds 60 seconds is terminated and returns `504 CONVERSION_TIMEOUT`
  4. An image-only (scanned) PDF that produces an empty DOCX returns `422 IMAGE_ONLY_PDF` with the temp file deleted
  5. All temp files are written only to the isolated temp directory using UUID filenames — never the original filename
**Plans**: TBD

Plans:
- [ ] 03-01: `services/validation.py` — magic byte check, size enforcement, MIME header check
- [ ] 03-02: `services/conversion.py` — pdf2docx primary, LibreOffice fallback, timeout watchdog, image-only detection
- [ ] 03-03: `core/registry.py` + `routers/convert.py` — job registry, concurrent job limit, convert endpoint wiring

### Phase 4: Download & Cleanup
**Goal**: Users receive their DOCX file as a browser download, the file is named meaningfully, and no files remain on the server after download
**Depends on**: Phase 3
**Requirements**: DWNL-01, DWNL-02, SECU-02, SECU-03
**Success Criteria** (what must be TRUE):
  1. After a successful conversion, the browser automatically triggers a file download named `{original_name}.docx` (e.g., `report.pdf` → `report.docx`)
  2. After the download completes, both the source PDF and the DOCX are deleted from the server's temp directory
  3. A TTL sweep running every 10 minutes deletes any job directories older than 60 minutes (orphaned files are removed even if the client never downloaded)
  4. Requesting a `job_id` that has already been downloaded returns `404 JOB_NOT_FOUND`
**Plans**: TBD

Plans:
- [ ] 04-01: `services/download.py` + `routers/download.py` — streaming DOCX delivery, derived filename, post-download cleanup
- [ ] 04-02: `core/cleanup.py` — TTL background sweep, orphaned file deletion, sweep logging

### Phase 5: Feedback & Polish
**Goal**: Users are informed at every stage of the workflow with clear, specific messages — and can recover from any error without refreshing the page
**Depends on**: Phase 4
**Requirements**: FDBK-01, FDBK-02, FDBK-03, FDBK-04
**Success Criteria** (what must be TRUE):
  1. The UI cycles through distinct visible states — Idle, Uploading (progress bar), Converting (spinner), Success (green tick + download prompt), Error (red alert) — with no state skipped
  2. Every server error code maps to a specific, plain-language message visible to the user (e.g., `IMAGE_ONLY_PDF` shows "This PDF contains only images and cannot be converted.")
  3. User can click "Try Again" from any error state and return to Idle without a page reload, with file input cleared
  4. A privacy statement ("Your file is deleted immediately after download — we never store your documents") is visible above the fold before any file is selected
  5. User can click "Convert Another File" after a successful download to return to Idle and start a new conversion
**Plans**: TBD

Plans:
- [ ] 05-01: `app.js` state machine — IDLE/UPLOADING/CONVERTING/SUCCESS/ERROR transitions, error message map, Try Again / Convert Another flow
- [ ] 05-02: `index.html` + `styles.css` — privacy statement, status banner, ARIA live regions, keyboard accessibility, colour-coded states

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/2 | Not started | - |
| 2. Upload Interface | 0/2 | Not started | - |
| 3. Conversion Engine | 0/3 | Not started | - |
| 4. Download & Cleanup | 0/2 | Not started | - |
| 5. Feedback & Polish | 0/2 | Not started | - |