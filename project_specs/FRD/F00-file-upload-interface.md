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
