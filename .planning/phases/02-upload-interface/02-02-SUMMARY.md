# Phase 02 Plan 02 — Summary

**Completed:** 2026-05-13
**Duration:** ~5 min
**Files modified:** app/static/app.js, e2e/upload-interface.spec.ts, app/static/styles.css (bug fix)

## State Machine Implemented

States: `IDLE` → `UPLOADING` → `CONVERTING` → `SUCCESS`
                                              ↘ `ERROR` → `IDLE` (Try Again)

| State | Trigger | Visual changes |
|-------|---------|----------------|
| IDLE | page load, Try Again, Convert Another | convert-btn disabled (if no file) |
| UPLOADING | convert-btn click | progress bar shown at 0%, status banner --uploading |
| CONVERTING | xhr.upload.onload (100% uploaded) | progress bar at 100, status banner --converting |
| SUCCESS | xhr.onload status 200 | status banner --success, convert-another-link shown |
| ERROR | xhr.onerror / non-200 response | status banner --error, error-detail + try-again-btn shown |

## XHR Implementation

- **Endpoint:** `POST /api/convert`
- **Method:** `XMLHttpRequest` (NOT fetch — required for upload.onprogress events)
- **Form data field:** `file` (via `FormData.append('file', selectedFile)`)
- **Progress:** `xhr.upload.onprogress` updates `#upload-progress` value 0→100
- **Download trigger:** `triggerDownload(job_id, filename)` — invisible `<a download>` click

## Error Message Strings (exact values — Phase 5 reference)

```javascript
INVALID_FILE_TYPE:  'The server rejected this file. Please select a valid PDF.'
FILE_TOO_LARGE:     'File too large. Maximum size is 50 MB.'
CONVERSION_TIMEOUT: 'Conversion timed out. Please try again with a smaller file.'
CONVERSION_FAILED:  'Conversion failed. Please try a different PDF file.'
IMAGE_ONLY_PDF:     'This PDF contains only images and cannot be converted.'
SERVER_BUSY:        'Server is busy. Please wait a moment and try again.'
INTERNAL_ERROR:     'An unexpected server error occurred. Please try again.'
JOB_NOT_FOUND:      'Download link expired. Please convert the file again.'
JOB_FAILED:         'Conversion job failed. Please try again.'
INVALID_JOB_ID:     'Invalid job reference. Please try again.'
```

Client-side inline error for type: `'Please select a PDF file.'`
Client-side inline error for size: `'File too large. Maximum size is 50 MB.'`

## Playwright Test Results

**15/15 tests pass** (0 failing, 0 skipped)

Test coverage:
- File picker: enables convert button on valid PDF
- Convert button disabled by default
- Drop zone ARIA attributes (tabindex, role)
- Drag-over CSS class applied/removed
- File drop shows filename and size
- Non-PDF (txt) → type error, button disabled, file-info hidden
- .docx file → type error
- 52,428,801 byte file → size error
- 50 MB hint visible in IDLE
- Progress bar hidden in IDLE
- Convert click → XHR request to /api/convert → ERROR state (backend mocked)
- Drop zone ARIA attributes
- Status banner aria-live + aria-atomic
- Try Again → IDLE reset (file info hidden, error hidden, convert disabled)

## Deviations from Plan

1. **Static file paths:** HTML uses `/static/styles.css` and `/static/app.js` (not relative `styles.css`) to match FastAPI's static mount at `/static`.
2. **CSS `[hidden]` override:** Added `[hidden] { display: none !important; }` rule to styles.css — required because `.file-info { display: flex }` and other display-setting rules would override the browser's default `hidden` attribute behaviour, causing Playwright's `not.toBeVisible()` checks to fail.
