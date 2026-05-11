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
   - Execute: `libreoffice --headless --convert-to docx {source_path} --outdir {job_dir}` via `subprocess.run` with a 60-second timeout.
   - If fallback also fails or times out → return `422 UNPROCESSABLE_ENTITY` with error code `CONVERSION_FAILED`; delete temp files.
8. **Image-only PDF detection:**
   - Inspect output DOCX: if it contains zero paragraphs with text content → return `422 UNPROCESSABLE_ENTITY` with error code `IMAGE_ONLY_PDF`; delete temp files.
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
