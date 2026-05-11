# PDF to DOCX Converter

## What This Is

A minimal web application that converts PDF files to DOCX (Microsoft Word) format. Users upload a PDF, the app processes the conversion, and they download the resulting DOCX file. The focus is simplicity and reliability — no accounts, no frills, just accurate conversion.

## Core Value

A user can upload any PDF and receive a faithful DOCX conversion they can edit in Word.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can upload a PDF file via the browser
- [ ] App converts the uploaded PDF to DOCX format
- [ ] User can download the converted DOCX file
- [ ] Conversion preserves text content and basic formatting (headings, paragraphs, lists)
- [ ] User receives clear feedback during upload and conversion progress
- [ ] User receives a meaningful error message if conversion fails

### Out of Scope

- User accounts / authentication — not needed for minimal conversion tool
- Batch conversion of multiple files simultaneously — adds complexity, defer to v2
- Cloud storage of uploaded files — files processed in memory / temp storage only
- OCR for scanned/image-based PDFs — significantly increases scope, defer to v2
- Editing PDFs before conversion — out of scope for a converter tool
- Mobile native apps — web-first approach sufficient

## Context

- This is a greenfield project with no existing codebase
- PDF-to-DOCX conversion is a well-understood problem with existing libraries (e.g., python-docx, pdf2docx, LibreOffice headless)
- The primary user is anyone who has a PDF they need to edit in Word
- File handling security (size limits, type validation) is important even for a minimal tool

## Constraints

- **Scope**: Minimal — single-feature tool, no user accounts, no persistence
- **Tech**: Server-side conversion required (browser cannot convert PDF to DOCX natively)
- **Privacy**: Uploaded files should not be stored permanently — delete after conversion

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Server-side conversion | PDF-to-DOCX requires native libraries not available in browser | — Pending |
| No user authentication | Minimal scope — anonymous uploads sufficient for v1 | — Pending |
| Temp file handling | Files deleted after download to protect user privacy | — Pending |

---
*Last updated: 2026-05-11 after initialization*
