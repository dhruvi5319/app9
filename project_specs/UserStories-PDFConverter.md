# User Stories
# PDF to DOCX Converter (PDFConverter)

**Version:** 1.0
**Date:** 2026-05-12
**Status:** Draft
**Based on:** PRD-PDFConverter.md v1.0, FRD-PDFConverter.md v1.0, PERSONAS-PDFConverter.md v1.0

---

## Personas

| ID | Name | Role |
|---|---|---|
| PER-01 | Marcus Webb | Office Professional |
| PER-02 | Priya Nair | Student / Academic |
| PER-03 | Dana Okafor | Freelancer / Small Business Owner |

---

## Priority Definitions

| Priority | Label | Description |
|---|---|---|
| **P0** | Critical | Required for MVP; product does not ship without it |
| **P1** | High | Important for user satisfaction; ship in v1 if possible |
| **P2** | Medium | Enhances experience; can defer to v1.1 |
| **P3** | Low | Nice-to-have; defer to future iteration |

---

## Table of Contents

- [Epic 0: File Upload Interface (F0)](#epic-0-file-upload-interface-f0)
- [Epic 1: Server-Side PDF-to-DOCX Conversion (F1)](#epic-1-server-side-pdf-to-docx-conversion-f1)
- [Epic 2: DOCX File Download (F2)](#epic-2-docx-file-download-f2)
- [Epic 3: User Feedback & Status Communication (F3)](#epic-3-user-feedback--status-communication-f3)
- [Epic 4: File Security & Privacy Controls (F4)](#epic-4-file-security--privacy-controls-f4)
- [Story Index](#story-index)

---

## Epic 0: File Upload Interface (F0)

*The primary user entry point. A clean, minimal web page with a file upload control (picker and drag-and-drop) that accepts a single PDF, performs client-side validation, shows upload progress, and triggers the conversion workflow.*

---

### US-0.1: Select a PDF via File Picker
**As a** Marcus Webb (office professional), **I want to** select a PDF file from my computer using a standard file picker, **so that** I can initiate a conversion without needing to install any software.

**Acceptance Criteria:**
- [ ] A file picker button/control is prominently displayed on the page
- [ ] The file picker filters to `.pdf` files by default (`accept=".pdf,application/pdf"`)
- [ ] After selecting a valid PDF, the filename and human-readable file size (e.g., "12.3 MB") are displayed in the UI
- [ ] The "Convert to DOCX" button becomes enabled only after a valid file is selected
- [ ] Selecting a new file replaces the previous selection and re-runs validation

**Priority:** P0 | **Feature Ref:** F0

---

### US-0.2: Upload PDF via Drag-and-Drop
**As a** Dana Okafor (freelancer), **I want to** drag a PDF file directly onto the upload area, **so that** I can start conversion faster without opening a file picker dialog.

**Acceptance Criteria:**
- [ ] A visually designated drop zone is displayed on the page
- [ ] Dragging a file over the drop zone provides a visible hover/highlight state
- [ ] Default browser drag-over behaviour (opening file in new tab) is prevented
- [ ] Dropping a PDF file onto the drop zone triggers the same validation as the file picker
- [ ] Dropping a non-PDF file displays the inline error "Please select a PDF file."

**Priority:** P0 | **Feature Ref:** F0

---

### US-0.3: Client-Side File Type Validation
**As a** Priya Nair (student), **I want to** receive an immediate error if I accidentally select a non-PDF file, **so that** I know right away what went wrong without waiting for a server round-trip.

**Acceptance Criteria:**
- [ ] When a non-PDF file is selected, the inline error "Please select a PDF file." is shown immediately
- [ ] Validation checks both `file.type === "application/pdf"` and that the filename ends with `.pdf` (case-insensitive)
- [ ] The "Convert to DOCX" button remains disabled when an invalid file type is selected
- [ ] The error message clears and validation re-runs if the user selects a different file

**Priority:** P0 | **Feature Ref:** F0

---

### US-0.4: Client-Side File Size Guard
**As a** Dana Okafor (freelancer), **I want to** be told immediately if my PDF is too large to upload, **so that** I don't waste time waiting for a slow upload that will be rejected.

**Acceptance Criteria:**
- [ ] Files exceeding 50 MB (52,428,800 bytes) are rejected before the upload begins
- [ ] The inline error "File too large. Maximum size is 50 MB." is displayed immediately on selection
- [ ] The "Convert to DOCX" button remains disabled for oversized files
- [ ] The maximum file size limit is communicated in the UI before the user selects a file (e.g., as a hint label)

**Priority:** P0 | **Feature Ref:** F0

---

### US-0.5: Upload Progress Indicator
**As a** Marcus Webb (office professional), **I want to** see a progress bar while my PDF is uploading, **so that** I know the upload is proceeding and haven't missed any feedback.

**Acceptance Criteria:**
- [ ] When the user clicks "Convert to DOCX", a progress bar initialises at 0% and is immediately visible
- [ ] The progress bar updates continuously from 0% to 100% as bytes are transmitted
- [ ] The "Convert to DOCX" button is disabled and shows a spinner during upload
- [ ] The upload form is locked (no new file can be selected) while upload is in progress
- [ ] On upload completion, the UI transitions to the "Converting…" state

**Priority:** P0 | **Feature Ref:** F0

---

### US-0.6: Keyboard-Accessible Upload Interface
**As a** Priya Nair (student), **I want to** operate the entire upload interface using only my keyboard, **so that** I can use the tool on shared lab computers without a mouse.

**Acceptance Criteria:**
- [ ] The file picker can be activated using `Enter` or `Space` when focused
- [ ] The "Convert to DOCX" button is keyboard-focusable and activatable via `Enter`
- [ ] All interactive elements follow a logical tab order
- [ ] Focus indicators are visibly distinct on all interactive elements
- [ ] The drop zone is reachable and usable via keyboard navigation

**Priority:** P0 | **Feature Ref:** F0

---

## Epic 1: Server-Side PDF-to-DOCX Conversion (F1)

*The core processing engine. The server validates the uploaded PDF, writes it to a secure temp directory, and invokes `pdf2docx` (with LibreOffice headless as fallback) to produce a DOCX file within a 60-second timeout.*

---

### US-1.1: Convert a Text-Based PDF to DOCX
**As a** Marcus Webb (office professional), **I want to** have my uploaded PDF converted to a DOCX file on the server, **so that** I can open and edit it in Microsoft Word.

**Acceptance Criteria:**
- [ ] The server accepts the uploaded PDF and initiates conversion via `pdf2docx`
- [ ] The converted DOCX is stored in a temp directory under a UUID-based job ID
- [ ] On successful conversion, the server returns a `200 OK` JSON response containing `job_id`, `filename`, and `file_size_bytes`
- [ ] For a standard text-based PDF (see definition below), text content, paragraph structure, headings, and lists are present in the output DOCX on a best-effort basis — the conversion library's output is accepted as-is without post-processing guarantees; a successful conversion is one where the output DOCX is non-empty and openable in Word
- [ ] Conversion completes within 60 seconds for PDFs up to 25 pages

**Definition — "standard text-based PDF":** A PDF whose pages consist primarily of a text layer (not rasterised images), generated by a standard application (e.g., Microsoft Word, Google Docs, LibreOffice, or a PDF printer). Complex layouts (multi-column magazine-style, heavily nested tables, embedded forms, or custom font subsets) are explicitly out of scope for formatting-quality guarantees.

**Priority:** P0 | **Feature Ref:** F1

---

### US-1.2: Fallback Conversion via LibreOffice
**As a** Dana Okafor (freelancer), **I want** the server to attempt a fallback conversion method if the primary converter fails, **so that** I have the best possible chance of getting a usable DOCX even from complex PDFs.

**Acceptance Criteria:**
- [ ] If `pdf2docx` raises an exception, the server automatically invokes LibreOffice headless as a fallback
- [ ] The fallback conversion also respects the 60-second timeout
- [ ] If both `pdf2docx` and LibreOffice fail, the server returns `422` with error code `CONVERSION_FAILED`
- [ ] The fallback attempt is transparent to the user — no additional action is required

**Priority:** P0 | **Feature Ref:** F1

---

### US-1.3: Conversion Timeout Enforcement
**As a** Dana Okafor (freelancer), **I want** a clear error message if my PDF is too complex to convert within the time limit, **so that** I can try a different file or tool rather than waiting indefinitely.

**Acceptance Criteria:**
- [ ] The server enforces a hard 60-second timeout on every conversion job
- [ ] If the timeout expires, the conversion process is terminated
- [ ] The server returns `504` with error code `CONVERSION_TIMEOUT`
- [ ] All temp files for the timed-out job are deleted before the error response is returned
- [ ] The user-facing error message explains the time limit was exceeded and suggests trying a smaller document

**Priority:** P0 | **Feature Ref:** F1

---

### US-1.4: Image-Only PDF Detection
**As a** Priya Nair (student), **I want** to receive a specific error message if my PDF is a scanned image, **so that** I understand why the conversion produced no text rather than receiving a blank DOCX silently.

**Acceptance Criteria:**
- [ ] After conversion, the server inspects the output DOCX for non-whitespace text content
- [ ] If the output DOCX contains no paragraph with at least one non-whitespace character (empty table cells, whitespace-only paragraphs, and line-break-only runs do not count), the server returns `422` with error code `IMAGE_ONLY_PDF`
- [ ] The empty DOCX is not served to the client
- [ ] All temp files for the job are deleted before the error response is returned
- [ ] The user-facing message explicitly states that scanned/image PDFs are not supported in this version

**Priority:** P0 | **Feature Ref:** F1

---

### US-1.5: Server-Side File Validation Before Conversion
**As a** Marcus Webb (office professional), **I want** the server to verify my uploaded file is genuinely a PDF before processing it, **so that** I receive a clear rejection rather than a confusing conversion error for the wrong file type.

**Acceptance Criteria:**
- [ ] The server reads the first 8 bytes of the uploaded file and checks for `%PDF` magic bytes
- [ ] If magic byte check fails, the server returns `400` with error code `INVALID_FILE_TYPE` and does not write the file to disk
- [ ] If the uploaded file exceeds 50 MB server-side, the server returns `413` with error code `FILE_TOO_LARGE`
- [ ] Server-side validation is independent of the client's declared `Content-Type` header
- [ ] All validation rejections discard the uploaded bytes without writing to disk

**Priority:** P0 | **Feature Ref:** F1

---

## Epic 2: DOCX File Download (F2)

*Upon successful conversion, the application delivers the converted DOCX as a file download with a meaningful filename, then immediately deletes both source and output temp files from the server.*

---

### US-2.1: Automatic DOCX Download After Conversion
**As a** Marcus Webb (office professional), **I want** the converted DOCX file to download automatically after conversion succeeds, **so that** I can get the file without any extra steps.

**Acceptance Criteria:**
- [ ] Immediately after the server returns a successful `job_id`, the client issues `GET /api/download/{job_id}`
- [ ] The browser opens a Save dialog or downloads the file without additional user interaction
- [ ] The response has `Content-Disposition: attachment` to force a download (never inline)
- [ ] The correct `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document` header is set
- [ ] A "Download DOCX" button is also rendered in the success state as an explicit alternative trigger

**Priority:** P0 | **Feature Ref:** F2

---

### US-2.2: Meaningful Download Filename
**As a** Marcus Webb (office professional), **I want** the downloaded DOCX file to be named after my original PDF, **so that** I can easily identify which document it corresponds to in my downloads folder.

**Acceptance Criteria:**
- [ ] The download filename is derived from the original PDF filename (e.g., `report.pdf` → `report.docx`)
- [ ] The filename derivation strips the `.pdf` extension and appends `.docx`
- [ ] Path separators (`/`, `\`), null bytes, and other unsafe characters are stripped from the derived filename
- [ ] The derived filename is limited to 255 characters
- [ ] The on-disk temp file uses the UUID job ID — the original filename is never written to the filesystem

**Priority:** P0 | **Feature Ref:** F2

---

### US-2.3: Post-Download Temp File Cleanup
**As a** Priya Nair (student), **I want** the server to delete my uploaded PDF and the converted DOCX immediately after I download the file, **so that** my document is not retained on any server after I have what I need.

**Acceptance Criteria:**
- [ ] Both the source `.pdf` and output `.docx` temp files are deleted from the server after the download response body is fully sent
- [ ] The job registry entry is updated to `COMPLETED` and files are marked as deleted
- [ ] A second download attempt for the same `job_id` returns `404` with error code `JOB_NOT_FOUND`
- [ ] If the client disconnects before download completes, the server still deletes the temp files
- [ ] `Cache-Control: no-store` is set on the download response to prevent proxy caching

**Priority:** P0 | **Feature Ref:** F2

---

### US-2.4: Handle Expired or Unknown Download Links
**As a** Dana Okafor (freelancer), **I want** a clear error message if my download link is no longer valid, **so that** I know I need to re-upload and convert the file rather than wondering if the download silently failed.

**Acceptance Criteria:**
- [ ] Requests for an unknown or expired `job_id` return `404` with error code `JOB_NOT_FOUND`
- [ ] Requests for a `job_id` still in `CONVERTING` state return `202` with status `"converting"`
- [ ] Requests for a `job_id` whose conversion failed return `410` with error code `JOB_FAILED`
- [ ] Requests with an invalid `job_id` format (not UUID v4) return `400` with error code `INVALID_JOB_ID`
- [ ] The user-facing error message explains the link has expired and prompts them to convert again

**Priority:** P0 | **Feature Ref:** F2

---

## Epic 3: User Feedback & Status Communication (F3)

*The application maintains a clear UI state machine (Idle → Uploading → Converting → Success/Error) with plain-language messages, progress indicators, and a retry flow at every stage.*

---

### US-3.1: Upload Progress Feedback
**As a** Marcus Webb (office professional), **I want to** see real-time upload progress while my file is being sent to the server, **so that** I know the upload is working and can estimate how long it will take.

**Acceptance Criteria:**
- [ ] The UI transitions from `IDLE` to `UPLOADING` state when the user clicks "Convert to DOCX"
- [ ] A progress bar is visible and updates continuously from 0% to 100% during upload
- [ ] The "Convert to DOCX" button is disabled and shows a spinner during upload
- [ ] If a network error occurs during upload, the UI transitions to `ERROR` with message "Upload failed. Please check your connection and try again."
- [ ] The progress bar and spinner are hidden in all non-`UPLOADING` states

**Priority:** P0 | **Feature Ref:** F3

---

### US-3.2: Conversion-in-Progress Status Indicator
**As a** Dana Okafor (freelancer), **I want to** see a clear "Converting…" indicator while the server processes my file, **so that** I know the system is working and haven't lost my conversion request.

**Acceptance Criteria:**
- [ ] When upload reaches 100%, the UI transitions from `UPLOADING` to `CONVERTING` state
- [ ] The `CONVERTING` state displays an animated spinner and the message "Converting your document…"
- [ ] The upload form and progress bar are hidden in the `CONVERTING` state
- [ ] The `CONVERTING` state persists until the server returns a success or error response (up to 60 seconds)
- [ ] State transitions follow the defined sequence — no state can be skipped (e.g., `IDLE` → `SUCCESS` is invalid)

**Priority:** P0 | **Feature Ref:** F3

---

### US-3.3: Conversion Success State
**As a** Marcus Webb (office professional), **I want to** see a clear success message and download prompt when my conversion is complete, **so that** I know the DOCX is ready and can retrieve it immediately.

**Acceptance Criteria:**
- [ ] When the server returns `200` with a `job_id`, the UI transitions to `SUCCESS` state
- [ ] The `SUCCESS` state displays a green tick icon and the message "Your DOCX is ready!"
- [ ] A "Download DOCX" button is displayed and triggers `GET /api/download/{job_id}` on click
- [ ] A "Convert Another File" link is displayed that resets the UI to `IDLE` without a page reload
- [ ] The success state is colour-coded green to distinguish it visually from error and progress states

**Priority:** P0 | **Feature Ref:** F3

---

### US-3.4: Actionable Error Messages
**As a** Priya Nair (student), **I want to** see a specific, plain-language error message when something goes wrong, **so that** I understand what happened and know whether and how to fix it.

**Acceptance Criteria:**
- [ ] Every server error code (`INVALID_FILE_TYPE`, `FILE_TOO_LARGE`, `CONVERSION_TIMEOUT`, `CONVERSION_FAILED`, `IMAGE_ONLY_PDF`, `SERVER_BUSY`, `INTERNAL_ERROR`, `JOB_NOT_FOUND`) maps to a distinct user-facing message
- [ ] The `ERROR` state displays a red alert icon, the primary error message, and a secondary error detail line
- [ ] Raw error codes, stack traces, and internal server details are never shown to the user
- [ ] A generic fallback message "Something went wrong on our end." is shown for any unmapped error code
- [ ] Error messages are colour-coded red to provide clear visual differentiation from success states

**Priority:** P0 | **Feature Ref:** F3

---

### US-3.5: Retry Without Page Reload
**As a** Dana Okafor (freelancer), **I want to** click "Try Again" after a failed conversion and immediately retry with a different file, **so that** I don't lose context or have to navigate back to the tool.

**Acceptance Criteria:**
- [ ] A "Try Again" button is displayed in the `ERROR` state
- [ ] Clicking "Try Again" resets the UI to `IDLE` state without a full page reload
- [ ] The file input field is cleared when "Try Again" is activated
- [ ] The progress bar, error messages, and status banners are hidden after reset
- [ ] The "Try Again" button is keyboard-focusable and activatable via `Enter`

**Priority:** P0 | **Feature Ref:** F3

---

### US-3.6: Screen Reader Accessibility for State Changes
**As a** Priya Nair (student), **I want** state transitions to be announced to assistive technologies, **so that** I can use the tool with a screen reader on shared lab computers.

**Acceptance Criteria:**
- [ ] State transitions are announced via ARIA live regions (`aria-live="polite"`) on the status banner
- [ ] Error messages in the `ERROR` state are surfaced to screen readers immediately
- [ ] The "Try Again" button and "Convert Another File" link are accessible via assistive technology
- [ ] All informational icons (green tick, red alert) have accessible text alternatives (`aria-label` or `alt`)
- [ ] Status messages do not rely on colour alone to convey meaning

**Priority:** P0 | **Feature Ref:** F3

---

## Epic 4: File Security & Privacy Controls (F4)

*Strict input validation, UUID-based temp file naming, immediate post-download cleanup, a TTL background sweep for orphaned files, and a concurrent job limit — ensuring no file persists beyond its conversion transaction.*

---

### US-4.1: Server-Side MIME Validation Regardless of Client Claims
**As a** Priya Nair (student), **I want** the server to independently verify my file is a real PDF using its content, **so that** I am protected from submitting the wrong file and the server is protected from malicious uploads.

**Acceptance Criteria:**
- [ ] The server reads the first 8 bytes of every uploaded file and checks for `%PDF` magic bytes
- [ ] Files failing the magic byte check are rejected with `400 INVALID_FILE_TYPE` before being written to disk
- [ ] The magic byte check is performed regardless of the `Content-Type` header declared by the client
- [ ] Server-side size enforcement (50 MB hard cap) is applied independently of any client-side check
- [ ] Files exceeding the server-side size limit return `413 FILE_TOO_LARGE`

**Priority:** P0 | **Feature Ref:** F4

---

### US-4.2: UUID-Based Temp File Naming to Prevent Path Traversal
**As a** Marcus Webb (office professional), **I want** my file to be stored under a server-generated name rather than its original filename, **so that** my document's filename cannot be used to attack the server or expose other users' files.

**Acceptance Criteria:**
- [ ] Every accepted conversion job is assigned a UUID v4 `job_id` before any file is written to disk
- [ ] Temp files are stored as `{TEMP_DIR}/{job_id}/{job_id}.pdf` and `{TEMP_DIR}/{job_id}/{job_id}.docx`
- [ ] The original uploaded filename is never used as the on-disk file name
- [ ] The original filename is never passed to any shell command
- [ ] Temp file permissions are set to `600` (owner read/write only); directory permissions are `700`

**Priority:** P0 | **Feature Ref:** F4

---

### US-4.3: Immediate Temp File Deletion After Download
**As a** Priya Nair (student), **I want** my files to be deleted from the server as soon as I download the DOCX, **so that** I can be confident no copy of my document remains on any third-party server after I have what I need.

**Acceptance Criteria:**
- [ ] Both the source `.pdf` and output `.docx` are deleted from the temp directory immediately after the download response body is fully sent
- [ ] Temp files for failed conversion jobs are deleted before the error response is returned
- [ ] No file or document metadata is logged by the server
- [ ] The UI confirms (via success state messaging) that the file has been delivered and is no longer stored (e.g., "Your file has been deleted from our server")
- [ ] A second request for the same `job_id` after cleanup returns `404 JOB_NOT_FOUND`
- [ ] A plain-language privacy disclosure statement (e.g., "Your file is deleted from our server immediately after you download it — we never store or log your documents") is visible on the upload page **above the fold and before any file is selected**, without requiring the user to scroll, click, or open a link

**Priority:** P0 | **Feature Ref:** F4

---

### US-4.4: TTL Background Sweep for Orphaned Files
**As a** Priya Nair (student), **I want** the server to automatically clean up any files left behind by interrupted sessions, **so that** my uploaded document is never retained indefinitely even if my browser crashes mid-download.

**Acceptance Criteria:**
- [ ] A background TTL sweep runs on a configurable schedule (default: every 10 minutes)
- [ ] The sweep deletes any temp subdirectory older than 60 minutes
- [ ] The sweep logs only the count of directories deleted and bytes freed — no file content or identifying metadata is logged
- [ ] The TTL duration and sweep interval are configurable via environment variables (`TTL_MINUTES`, `SWEEP_INTERVAL_MINUTES`)
- [ ] The sweep correctly handles the case where the server restarts with orphaned files from a prior session

**Priority:** P0 | **Feature Ref:** F4

---

### US-4.5: Concurrent Job Limit to Prevent Resource Exhaustion
**As a** Dana Okafor (freelancer), **I want** the server to gracefully handle high load rather than slow down or crash, **so that** my conversions complete reliably even during peak usage.

**Acceptance Criteria:**
- [ ] The server enforces a configurable maximum of concurrent active conversion jobs (default: 5)
- [ ] When the job limit is reached, new requests return `503` with error code `SERVER_BUSY`
- [ ] The `SERVER_BUSY` error code maps to the user-facing message "The server is busy. Please try again in a moment."
- [ ] The active job counter is correctly incremented on job acceptance and decremented on job completion (success, failure, or timeout)
- [ ] The concurrent job limit is configurable via the `MAX_CONCURRENT_JOBS` environment variable

**Priority:** P0 | **Feature Ref:** F4

---

### US-4.6: No Logging of File Content or User-Identifying Metadata
**As a** Marcus Webb (office professional), **I want** to be confident that the server never logs the contents of my uploaded documents, **so that** I can safely convert confidential contracts without a compliance risk.

**Acceptance Criteria:**
- [ ] Server logs do not contain file content, original filenames, or any metadata that could identify a user or their document
- [ ] Conversion duration and outcome (success/failure) may be logged, but only with the `job_id` — no user-facing data
- [ ] Error logs produced during conversion do not capture document content
- [ ] No analytics or third-party tracking scripts are included that could intercept file data
- [ ] The no-logging guarantee is reflected in the product's stated privacy behaviour communicated via the UI

**Priority:** P0 | **Feature Ref:** F4

---

## Story Index

| Story ID | Title | Persona | Priority | Feature Ref |
|---|---|---|---|---|
| US-0.1 | Select a PDF via File Picker | Marcus Webb | P0 | F0 |
| US-0.2 | Upload PDF via Drag-and-Drop | Dana Okafor | P0 | F0 |
| US-0.3 | Client-Side File Type Validation | Priya Nair | P0 | F0 |
| US-0.4 | Client-Side File Size Guard | Dana Okafor | P0 | F0 |
| US-0.5 | Upload Progress Indicator | Marcus Webb | P0 | F0 |
| US-0.6 | Keyboard-Accessible Upload Interface | Priya Nair | P0 | F0 |
| US-1.1 | Convert a Text-Based PDF to DOCX | Marcus Webb | P0 | F1 |
| US-1.2 | Fallback Conversion via LibreOffice | Dana Okafor | P0 | F1 |
| US-1.3 | Conversion Timeout Enforcement | Dana Okafor | P0 | F1 |
| US-1.4 | Image-Only PDF Detection | Priya Nair | P0 | F1 |
| US-1.5 | Server-Side File Validation Before Conversion | Marcus Webb | P0 | F1 |
| US-2.1 | Automatic DOCX Download After Conversion | Marcus Webb | P0 | F2 |
| US-2.2 | Meaningful Download Filename | Marcus Webb | P0 | F2 |
| US-2.3 | Post-Download Temp File Cleanup | Priya Nair | P0 | F2 |
| US-2.4 | Handle Expired or Unknown Download Links | Dana Okafor | P0 | F2 |
| US-3.1 | Upload Progress Feedback | Marcus Webb | P0 | F3 |
| US-3.2 | Conversion-in-Progress Status Indicator | Dana Okafor | P0 | F3 |
| US-3.3 | Conversion Success State | Marcus Webb | P0 | F3 |
| US-3.4 | Actionable Error Messages | Priya Nair | P0 | F3 |
| US-3.5 | Retry Without Page Reload | Dana Okafor | P0 | F3 |
| US-3.6 | Screen Reader Accessibility for State Changes | Priya Nair | P0 | F3 |
| US-4.1 | Server-Side MIME Validation Regardless of Client Claims | Priya Nair | P0 | F4 |
| US-4.2 | UUID-Based Temp File Naming to Prevent Path Traversal | Marcus Webb | P0 | F4 |
| US-4.3 | Immediate Temp File Deletion After Download | Priya Nair | P0 | F4 |
| US-4.4 | TTL Background Sweep for Orphaned Files | Priya Nair | P0 | F4 |
| US-4.5 | Concurrent Job Limit to Prevent Resource Exhaustion | Dana Okafor | P0 | F4 |
| US-4.6 | No Logging of File Content or User-Identifying Metadata | Marcus Webb | P0 | F4 |

**Total Stories:** 27 across 5 epics | **All priorities:** P0 (Critical — all features are MVP requirements)

---

*Document generated: 2026-05-12 | Project: PDFConverter | Version: 1.0*
*Derived from PRD-PDFConverter.md v1.0, FRD-PDFConverter.md v1.0, PERSONAS-PDFConverter.md v1.0*
