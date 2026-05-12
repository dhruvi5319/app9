# Requirements: PDF to DOCX Converter

**Defined:** 2026-05-12
**Core Value:** A user can upload any PDF and receive a faithful DOCX conversion they can edit in Word.

## v1 Requirements

### File Upload

- [ ] **UPLD-01**: User can select a PDF file via drag-and-drop onto the upload zone
- [ ] **UPLD-02**: User can select a PDF file via a file picker button
- [ ] **UPLD-03**: User receives an immediate client-side error if a non-PDF file is selected
- [ ] **UPLD-04**: User receives an immediate client-side error if the file exceeds the size limit (50 MB)
- [ ] **UPLD-05**: User sees an upload progress indicator while the file is being sent to the server

### Conversion

- [ ] **CONV-01**: Server converts the uploaded PDF to DOCX format using pdf2docx (with LibreOffice headless fallback)
- [ ] **CONV-02**: Conversion fails gracefully with a clear error if it exceeds 60 seconds
- [ ] **CONV-03**: Server detects image-only / scanned PDFs and returns a specific error explaining the limitation

### Download

- [ ] **DWNL-01**: User's browser automatically triggers a DOCX file download upon successful conversion
- [ ] **DWNL-02**: The downloaded DOCX filename is derived from the original PDF filename (e.g. `report.pdf` → `report.docx`)

### Feedback & Status

- [ ] **FDBK-01**: UI displays distinct states for idle, uploading, converting, success, and error
- [ ] **FDBK-02**: Every error state shows a specific, actionable next-step message (not a generic error)
- [ ] **FDBK-03**: User can reset to idle and convert another file after a successful conversion
- [ ] **FDBK-04**: A plain-language privacy statement ("Your file is deleted immediately after download — we never store your documents") is visible above the fold before any file is selected

### Security & Privacy

- [ ] **SECU-01**: Server validates uploaded file using MIME type and magic bytes — rejects non-PDF files
- [ ] **SECU-02**: Converted DOCX temp file is deleted from the server immediately after the user downloads it
- [ ] **SECU-03**: A TTL-based cleanup sweep deletes any unclaimed temp files after a configurable window (default: 30 minutes)
- [ ] **SECU-04**: No uploaded or converted file is written to persistent storage — all processing uses temp directories

## v2 Requirements

### Conversion Quality

- **CONV-V2-01**: OCR support for scanned / image-only PDFs
- **CONV-V2-02**: Post-conversion quality score or warning when formatting fidelity is low

### Batch Processing

- **BTCH-V2-01**: User can upload and convert multiple PDFs in a single session
- **BTCH-V2-02**: User can download all converted files as a ZIP archive

### Usability

- **USBL-V2-01**: User can preview the converted DOCX content in-browser before downloading
- **USBL-V2-02**: Conversion history stored locally (browser localStorage) for the session

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / authentication | Not needed — anonymous single-use tool |
| Persistent file storage | Privacy policy: zero retention in v1 |
| OAuth / social login | No accounts in scope |
| Mobile native app | Web-first; responsive web sufficient |
| Real-time collaborative editing | Out of scope for a converter |
| PDF editing before conversion | Different product category |
| Payments / subscriptions | Not needed for minimal v1 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| UPLD-01 | Phase 2 | Pending |
| UPLD-02 | Phase 2 | Pending |
| UPLD-03 | Phase 2 | Pending |
| UPLD-04 | Phase 2 | Pending |
| UPLD-05 | Phase 2 | Pending |
| CONV-01 | Phase 3 | Pending |
| CONV-02 | Phase 3 | Pending |
| CONV-03 | Phase 3 | Pending |
| DWNL-01 | Phase 4 | Pending |
| DWNL-02 | Phase 4 | Pending |
| FDBK-01 | Phase 5 | Pending |
| FDBK-02 | Phase 5 | Pending |
| FDBK-03 | Phase 5 | Pending |
| FDBK-04 | Phase 5 | Pending |
| SECU-01 | Phase 3 | Pending |
| SECU-02 | Phase 4 | Pending |
| SECU-03 | Phase 4 | Pending |
| SECU-04 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-12*
*Last updated: 2026-05-12 after initial definition*
