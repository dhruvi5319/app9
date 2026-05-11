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
| `ERROR` | Any error from client-side validation, upload, or server | Red alert icon + human-readable error message + error detail; "Try Again" button |

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
- **MUST** prevent state transitions that skip states (e.g., jumping from `IDLE` to `SUCCESS`).
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
