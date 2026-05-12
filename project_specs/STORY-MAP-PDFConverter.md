# Story Map
# PDF to DOCX Converter (PDFConverter)

| Field | Value |
|---|---|
| **Product Name** | PDFConverter |
| **Document Version** | 1.0 |
| **Date** | 2026-05-12 |
| **Status** | Draft |
| **Related Personas** | PERSONAS-PDFConverter.md v1.0 |
| **Related JTBD** | JTBD-PDFConverter.md v1.0 |
| **Related Journeys** | JOURNEYS-PDFConverter.md v1.0 |
| **Related UserStories** | UserStories-PDFConverter.md v1.0 |
| **Related PRD** | PRD-PDFConverter.md v1.0 |

---

## Overview

This Story Map organises the 27 user stories for PDFConverter onto a two-dimensional grid:

- **X-axis (columns):** Journey stages extracted from JOURNEYS-PDFConverter.md — the five stages every persona passes through in the core conversion workflow: **Arrive → Select/Upload → Convert → Download → Error/Retry**
- **Y-axis (rows):** Epics and individual stories within each stage, grouped by persona
- **NaC column:** Natural Acceptance Criteria derived from the intersection of a JTBD outcome and the journey stage context — these bridge the "why" (JTBD) to testable criteria that extend or reinforce the story's acceptance criteria
- **Release column:** All stories are assigned to **R1 (MVP)** — every feature is P0 and the product does not ship without any of them

### NaC Concept

A Natural Acceptance Criterion (NaC) is not invented. It is derived from three inputs:

1. **JTBD outcome** — what the user is trying to accomplish (the "what matters")
2. **Journey stage** — where in the workflow the story lives (the "when/where")
3. **User story** — what is being built (the "what")

The derivation chain is: `JTBD outcome × Journey stage → NaC statement`

NaC statements use Given/When/Then format to remain testable and unambiguous.

---

## Story Map Matrix

*All 27 stories are P0 / R1 (MVP). Journey stages are shared across all personas — the X-axis represents the canonical conversion workflow.*

### Stage Definitions

| Stage ID | Stage Name | Description | Primary Features |
|---|---|---|---|
| S1 | Arrive | User lands on the page; reads privacy disclosure; evaluates trust | F0, F4 |
| S2 | Select / Upload | User selects or drops a PDF; client-side validation fires; upload transmits | F0, F3 |
| S3 | Convert | Server processes the PDF; status indicator visible; user waits | F1, F3 |
| S4 | Download | Conversion succeeds; DOCX is delivered; temp files deleted | F2, F3, F4 |
| S5 | Error / Retry | Conversion or validation fails; specific error shown; in-place retry | F0, F3, F1 |

---

### Persona: PER-01 Marcus Webb (Office Professional)

| SM-ID | Story | Stage | Epic | NaC (derived) | Release |
|---|---|---|---|---|---|
| SM-0.1 | US-0.1: Select a PDF via File Picker | S2: Select/Upload | Epic 0 (F0) | JTBD-01.1 × S2 → File picker opens without install prompt; selected PDF filename and size appear in UI before upload begins | R1 |
| SM-0.5 | US-0.5: Upload Progress Indicator | S2: Select/Upload | Epic 0 (F0) | JTBD-01.1 × S2 → Progress bar increments continuously during upload; button is disabled; no silent hang | R1 |
| SM-1.1 | US-1.1: Convert a Text-Based PDF to DOCX | S3: Convert | Epic 1 (F1) | JTBD-01.1 × S3 → Server accepts upload and returns job_id; text, headings, and lists are present in output DOCX; completes within 60 seconds | R1 |
| SM-1.5 | US-1.5: Server-Side File Validation Before Conversion | S3: Convert | Epic 1 (F1) | JTBD-01.2 × S3 → Server rejects non-PDF or oversized file before conversion begins; error code and plain-language message returned immediately | R1 |
| SM-2.1 | US-2.1: Automatic DOCX Download After Conversion | S4: Download | Epic 2 (F2) | JTBD-01.1 × S4 → DOCX download is triggered automatically after success; no extra step required; full cycle ≤ 60 seconds from file selection | R1 |
| SM-2.2 | US-2.2: Meaningful Download Filename | S4: Download | Epic 2 (F2) | JTBD-01.1 × S4 → Downloaded file is named after the original PDF (e.g., contract.pdf → contract.docx); identifiable in downloads folder immediately | R1 |
| SM-3.1 | US-3.1: Upload Progress Feedback | S2: Select/Upload | Epic 3 (F3) | JTBD-01.1 × S2 → Upload progress bar updates in real time; button spinner visible; network error surfaces explicit message | R1 |
| SM-3.3 | US-3.3: Conversion Success State | S4: Download | Epic 3 (F3) | JTBD-01.1 × S4 → Green tick and "Your DOCX is ready!" appear; Download button and "Convert Another File" link are both visible | R1 |
| SM-4.2 | US-4.2: UUID-Based Temp File Naming | S3: Convert | Epic 4 (F4) | JTBD-01.3 × S3 → Original filename is never written to disk or passed to shell commands; job is identified by UUID only | R1 |
| SM-4.6 | US-4.6: No Logging of File Content or User Metadata | S3: Convert | Epic 4 (F4) | JTBD-01.3 × S3 → Server logs contain only job_id, duration, and outcome; no filename, file content, or user-identifying data appears in any log | R1 |

---

### Persona: PER-02 Priya Nair (Student / Academic)

| SM-ID | Story | Stage | Epic | NaC (derived) | Release |
|---|---|---|---|---|---|
| SM-0.3 | US-0.3: Client-Side File Type Validation | S2: Select/Upload | Epic 0 (F0) | JTBD-02.1 × S2 → Non-PDF selection shows inline error immediately; no server round-trip; works identically in Chrome, Firefox, Safari, and Edge | R1 |
| SM-0.6 | US-0.6: Keyboard-Accessible Upload Interface | S2: Select/Upload | Epic 0 (F0) | JTBD-02.1 × S2 → File picker activates on Enter/Space; tab order is logical; focus indicators are visible; full conversion cycle completable without mouse | R1 |
| SM-1.4 | US-1.4: Image-Only PDF Detection | S3: Convert | Epic 1 (F1) | JTBD-02.3 × S3 → When output DOCX has zero text paragraphs, server returns IMAGE_ONLY_PDF; no blank DOCX is served; error names scanned/image-only type explicitly | R1 |
| SM-2.3 | US-2.3: Post-Download Temp File Cleanup | S4: Download | Epic 2 (F2) | JTBD-01.3 × S4 → Source PDF and output DOCX are deleted immediately after download response is sent; second request for same job_id returns 404 | R1 |
| SM-3.4 | US-3.4: Actionable Error Messages | S5: Error/Retry | Epic 3 (F3) | JTBD-02.3 × S5 → Every server error code maps to a distinct plain-language message; IMAGE_ONLY_PDF error explicitly mentions scanned PDFs and suggests an OCR tool | R1 |
| SM-3.6 | US-3.6: Screen Reader Accessibility for State Changes | S3: Convert | Epic 3 (F3) | JTBD-02.1 × S3 → State transitions announced via aria-live; error messages surfaced to screen readers; icons have accessible text; no colour-only meaning | R1 |
| SM-4.1 | US-4.1: Server-Side MIME Validation | S2: Select/Upload | Epic 4 (F4) | JTBD-02.2 × S2 → Server reads magic bytes independently of Content-Type; non-PDF rejected before write to disk; 400 INVALID_FILE_TYPE returned | R1 |
| SM-4.3 | US-4.3: Immediate Temp File Deletion After Download | S4: Download | Epic 4 (F4) | JTBD-02.2 × S4 → UI success state confirms file is no longer stored; Cache-Control: no-store set on download response; deletion occurs even on client disconnect | R1 |
| SM-4.4 | US-4.4: TTL Background Sweep for Orphaned Files | S4: Download | Epic 4 (F4) | JTBD-02.2 × S4 → Files older than 60 minutes are deleted by background sweep; sweep logs only count and bytes, never content; configurable via env vars | R1 |

---

### Persona: PER-03 Dana Okafor (Freelancer / Small Business Owner)

| SM-ID | Story | Stage | Epic | NaC (derived) | Release |
|---|---|---|---|---|---|
| SM-0.2 | US-0.2: Upload PDF via Drag-and-Drop | S2: Select/Upload | Epic 0 (F0) | JTBD-03.2 × S2 → Drag-and-drop onto drop zone triggers same validation as file picker; hover state visible; default browser behaviour (open file in tab) prevented | R1 |
| SM-0.4 | US-0.4: Client-Side File Size Guard | S1: Arrive / S2: Select | Epic 0 (F0) | JTBD-03.3 × S1+S2 → Max file size (50 MB) displayed as static text before any file is selected; oversized file rejected within 2 seconds of selection; error states both file size and limit | R1 |
| SM-1.2 | US-1.2: Fallback Conversion via LibreOffice | S3: Convert | Epic 1 (F1) | JTBD-03.1 × S3 → If pdf2docx fails, LibreOffice headless is tried automatically; fallback is transparent to user; both fail → 422 CONVERSION_FAILED | R1 |
| SM-1.3 | US-1.3: Conversion Timeout Enforcement | S3: Convert | Epic 1 (F1) | JTBD-03.2 × S3 → Hard 60-second timeout terminates runaway jobs; 504 CONVERSION_TIMEOUT returned; temp files cleaned up; user message suggests trying smaller document | R1 |
| SM-2.4 | US-2.4: Handle Expired or Unknown Download Links | S5: Error/Retry | Epic 2 (F2) | JTBD-01.2 × S5 → Expired job_id returns 404 JOB_NOT_FOUND; in-progress job returns 202; failed job returns 410; user message prompts re-upload | R1 |
| SM-3.2 | US-3.2: Conversion-in-Progress Status Indicator | S3: Convert | Epic 3 (F3) | JTBD-03.2 × S3 → Animated "Converting your document…" spinner visible throughout server processing; UI does not require focus to complete; state persists until response received | R1 |
| SM-3.5 | US-3.5: Retry Without Page Reload | S5: Error/Retry | Epic 3 (F3) | JTBD-01.2 × S5 → "Try Again" button resets UI to IDLE in-place; file input cleared; no page navigation; keyboard-focusable | R1 |
| SM-4.5 | US-4.5: Concurrent Job Limit | S3: Convert | Epic 4 (F4) | JTBD-03.2 × S3 → Server returns 503 SERVER_BUSY when max concurrent jobs reached; counter increments/decrements correctly; user sees "try again in a moment" message | R1 |

---

## NaC Derivation Table

Full traceability chain: JTBD outcome → Journey stage → NaC statement → Story

| NaC-ID | JTBD-ID | JTBD Outcome (abbreviated) | Journey Stage | NaC Statement | Story |
|---|---|---|---|---|---|
| NaC-01 | JTBD-01.1 | Full cycle ≤ 60s, no account, no install | S2: Select/Upload | File picker opens without any install or sign-up prompt; selected filename and size are displayed before upload begins | US-0.1 |
| NaC-02 | JTBD-01.1 | Full cycle ≤ 60s; progress visible | S2: Select/Upload | Progress bar increments continuously 0%→100% during upload; button disabled with spinner; no silent hang state | US-0.5, US-3.1 |
| NaC-03 | JTBD-01.1 | Formatting preserved; completes ≤ 60s | S3: Convert | Server returns job_id within 60 seconds; output DOCX contains text, heading hierarchy, and list structure matching source PDF | US-1.1 |
| NaC-04 | JTBD-01.1 | DOCX downloaded automatically | S4: Download | DOCX download triggers immediately after job_id returned; full upload→download cycle completes ≤ 60 seconds from file selection | US-2.1 |
| NaC-05 | JTBD-01.1 | File identifiable after download | S4: Download | Downloaded file is named `{original_name}.docx`; identifiable in downloads folder without manual rename | US-2.2 |
| NaC-06 | JTBD-01.1 | Success state clear and unambiguous | S4: Download | Green tick and "Your DOCX is ready!" message appear; Download button and "Convert Another File" link both visible | US-3.3 |
| NaC-07 | JTBD-01.2 | Specific error + retry path | S3: Convert | Server rejects non-PDF or oversized file before conversion; specific error code and plain-language message returned; no partial processing | US-1.5 |
| NaC-08 | JTBD-01.2 | Error understood within 30 seconds | S5: Error/Retry | Every server error code maps to a unique user-facing message with cause and next step; no raw codes or stack traces shown | US-3.4 |
| NaC-09 | JTBD-01.2 | Retry in-place, no context lost | S5: Error/Retry | "Try Again" resets UI to IDLE without page reload; file input cleared; keyboard-accessible | US-3.5 |
| NaC-10 | JTBD-01.2 | Expired link explained | S5: Error/Retry | Expired job_id returns 404 with user message prompting re-upload; in-progress returns 202; no silent failure | US-2.4 |
| NaC-11 | JTBD-01.3 | Files deleted post-download; UI confirms | S4: Download | Source PDF and DOCX deleted immediately after download response sent; UI success message confirms deletion; Cache-Control: no-store set | US-2.3, US-4.3 |
| NaC-12 | JTBD-01.3 | No file metadata in logs | S3: Convert | Server logs contain only job_id, duration, outcome; no filename, content, or user-identifying data in any log or analytics | US-4.6 |
| NaC-13 | JTBD-01.3 | UUID naming prevents original filename exposure | S3: Convert | Original filename never written to disk or passed to shell; on-disk file is `{job_id}.pdf` / `{job_id}.docx` | US-4.2 |
| NaC-14 | JTBD-02.1 | Works on any current browser, no install | S2: Select/Upload | File type validation error appears inline immediately in Chrome, Firefox, Safari, and Edge without browser extension | US-0.3 |
| NaC-15 | JTBD-02.1 | Fully keyboard-navigable | S2: Select/Upload | File picker activates on Enter/Space; tab order logical; focus indicators visible; full cycle completable keyboard-only | US-0.6 |
| NaC-16 | JTBD-02.1 | State changes accessible to screen readers | S3: Convert | aria-live regions announce all state transitions; error messages surfaced immediately; icons have accessible text | US-3.6 |
| NaC-17 | JTBD-02.2 | Privacy disclosure visible before interaction | S1: Arrive | Plain-language file deletion statement visible above fold before any file is selected; no external link required to read it | US-4.3, US-4.6 |
| NaC-18 | JTBD-02.2 | Server validates independently of client | S2: Select/Upload | Server reads magic bytes regardless of Content-Type; non-PDF rejected before write to disk; 400 INVALID_FILE_TYPE returned | US-4.1 |
| NaC-19 | JTBD-02.2 | Files deleted even on interrupted sessions | S4: Download | TTL background sweep deletes files older than 60 minutes; sweep logs only count and bytes; configurable via env vars | US-4.4 |
| NaC-20 | JTBD-02.3 | Scanned PDF triggers specific error | S3: Convert | IMAGE_ONLY_PDF error returned when output DOCX has zero text; error names scanned/image-only explicitly; no blank DOCX served | US-1.4 |
| NaC-21 | JTBD-02.3 | Error suggests concrete next step | S5: Error/Retry | IMAGE_ONLY_PDF user message explains OCR not supported and names at least one OCR tool alternative | US-3.4 |
| NaC-22 | JTBD-03.1 | Tables, lists, headings preserved | S3: Convert | If pdf2docx fails, LibreOffice headless invoked automatically; both fallback attempts preserve structure before returning CONVERSION_FAILED | US-1.2 |
| NaC-23 | JTBD-03.2 | Conversion ≤ 15s median; tab-independent | S3: Convert | Animated "Converting…" spinner visible throughout; conversion completes whether or not user stays on tab | US-3.2 |
| NaC-24 | JTBD-03.2 | Timeout handled gracefully | S3: Convert | 60-second hard timeout terminates job; 504 CONVERSION_TIMEOUT returned; temp files cleaned; user message suggests smaller file | US-1.3 |
| NaC-25 | JTBD-03.2 | Server stays reliable under load | S3: Convert | 503 SERVER_BUSY returned when concurrent job limit reached; counter increments/decrements correctly; user message actionable | US-4.5 |
| NaC-26 | JTBD-03.3 | Size limit visible before file selection | S1: Arrive | "Maximum file size: 50 MB" displayed as static text near upload control; visible before any interaction | US-0.4 |
| NaC-27 | JTBD-03.3 | Oversized file rejected within 2 seconds | S2: Select/Upload | Client-side guard fires ≤ 2 seconds after file selection; error states both actual file size and limit; no bytes transmitted | US-0.4 |
| NaC-28 | JTBD-03.3 | Drag-and-drop same validation as picker | S2: Select/Upload | Drop zone highlights on hover; PDF dropped triggers identical validation; non-PDF drop shows inline error | US-0.2 |

---

## Release Planning

### R1: MVP — Complete End-to-End Conversion Workflow

**Theme:** Deliver the full upload → convert → download journey for all three personas, with no gaps in the critical path, error handling, or privacy guarantees.

**Rationale:** Every feature is P0 and every story is required for the product to ship. There are no P1/P2 stories to defer — this is a minimal, single-purpose tool where all 27 stories are load-bearing. Release grouping by journey completeness is the natural structure.

**Release Goal:** Any persona can arrive on the page, upload a PDF, receive a DOCX (or a specific, actionable error), and leave confident their file was not retained — all in under 60 seconds, on any modern browser, without an account.

---

#### R1 Story Roster by Journey Stage

| Stage | SM-ID | Story | Primary Persona |
|---|---|---|---|
| S1: Arrive | SM-0.4 (partial) | Client-Side File Size Guard (size hint display) | PER-03 Dana |
| S2: Select/Upload | SM-0.1 | Select a PDF via File Picker | PER-01 Marcus |
| S2: Select/Upload | SM-0.2 | Upload PDF via Drag-and-Drop | PER-03 Dana |
| S2: Select/Upload | SM-0.3 | Client-Side File Type Validation | PER-02 Priya |
| S2: Select/Upload | SM-0.4 | Client-Side File Size Guard (rejection) | PER-03 Dana |
| S2: Select/Upload | SM-0.5 | Upload Progress Indicator | PER-01 Marcus |
| S2: Select/Upload | SM-0.6 | Keyboard-Accessible Upload Interface | PER-02 Priya |
| S2: Select/Upload | SM-3.1 | Upload Progress Feedback | PER-01 Marcus |
| S2: Select/Upload | SM-4.1 | Server-Side MIME Validation | PER-02 Priya |
| S3: Convert | SM-1.1 | Convert a Text-Based PDF to DOCX | PER-01 Marcus |
| S3: Convert | SM-1.2 | Fallback Conversion via LibreOffice | PER-03 Dana |
| S3: Convert | SM-1.3 | Conversion Timeout Enforcement | PER-03 Dana |
| S3: Convert | SM-1.4 | Image-Only PDF Detection | PER-02 Priya |
| S3: Convert | SM-1.5 | Server-Side File Validation Before Conversion | PER-01 Marcus |
| S3: Convert | SM-3.2 | Conversion-in-Progress Status Indicator | PER-03 Dana |
| S3: Convert | SM-3.6 | Screen Reader Accessibility for State Changes | PER-02 Priya |
| S3: Convert | SM-4.2 | UUID-Based Temp File Naming | PER-01 Marcus |
| S3: Convert | SM-4.5 | Concurrent Job Limit | PER-03 Dana |
| S3: Convert | SM-4.6 | No Logging of File Content or User Metadata | PER-01 Marcus |
| S4: Download | SM-2.1 | Automatic DOCX Download After Conversion | PER-01 Marcus |
| S4: Download | SM-2.2 | Meaningful Download Filename | PER-01 Marcus |
| S4: Download | SM-2.3 | Post-Download Temp File Cleanup | PER-02 Priya |
| S4: Download | SM-3.3 | Conversion Success State | PER-01 Marcus |
| S4: Download | SM-4.3 | Immediate Temp File Deletion After Download | PER-02 Priya |
| S4: Download | SM-4.4 | TTL Background Sweep for Orphaned Files | PER-02 Priya |
| S5: Error/Retry | SM-2.4 | Handle Expired or Unknown Download Links | PER-03 Dana |
| S5: Error/Retry | SM-3.4 | Actionable Error Messages | PER-02 Priya |
| S5: Error/Retry | SM-3.5 | Retry Without Page Reload | PER-03 Dana |

**Total R1 stories:** 27 (all stories) | **Epics complete in R1:** 5 of 5

---

#### R1 Persona Coverage

| Persona | Journey Completed | JTBD Addressed | Stories in R1 |
|---|---|---|---|
| PER-01 Marcus Webb | JRN-01.1 (routine conversion) + JRN-01.2 (error recovery) | JTBD-01.1, JTBD-01.2, JTBD-01.3 | US-0.1, US-0.5, US-1.1, US-1.5, US-2.1, US-2.2, US-3.1, US-3.3, US-4.2, US-4.6 |
| PER-02 Priya Nair | JRN-02.1 (privacy check + form conversion) + JRN-02.2 (scanned PDF error) | JTBD-02.1, JTBD-02.2, JTBD-02.3 | US-0.3, US-0.6, US-1.4, US-2.3, US-3.4, US-3.6, US-4.1, US-4.3, US-4.4 |
| PER-03 Dana Okafor | JRN-03.1 (SoW conversion in workflow) + JRN-03.2 (oversized file rejection) | JTBD-03.1, JTBD-03.2, JTBD-03.3 | US-0.2, US-0.4, US-1.2, US-1.3, US-2.4, US-3.2, US-3.5, US-4.5 |

All three personas have complete journeys enabled by R1. No persona is partially served.

---

## Coverage Analysis

### Persona Coverage

| Persona | Journeys Mapped | Stories Mapped | JTBD Covered | Release |
|---|---|---|---|---|
| PER-01 Marcus Webb | JRN-01.1, JRN-01.2 | 10 stories | JTBD-01.1, JTBD-01.2, JTBD-01.3 (3/3) | R1 ✓ |
| PER-02 Priya Nair | JRN-02.1, JRN-02.2 | 9 stories | JTBD-02.1, JTBD-02.2, JTBD-02.3 (3/3) | R1 ✓ |
| PER-03 Dana Okafor | JRN-03.1, JRN-03.2 | 8 stories | JTBD-03.1, JTBD-03.2, JTBD-03.3 (3/3) | R1 ✓ |

> Note: Story counts sum to more than 27 because several stories serve multiple personas (e.g., US-3.4 is written for PER-02 but directly serves all three personas via shared error taxonomy). The 27 distinct stories in UserStories-PDFConverter.md are all mapped.

---

### JTBD Coverage

| JTBD-ID | Outcome (abbreviated) | Stories Addressing It | NaC Count | Coverage |
|---|---|---|---|---|
| JTBD-01.1 | Full cycle ≤ 60s, no account, formatting preserved | US-0.1, US-0.5, US-1.1, US-2.1, US-2.2, US-3.1, US-3.3 | 6 | ✓ Full |
| JTBD-01.2 | Specific error + in-place retry within 30s | US-1.5, US-2.4, US-3.4, US-3.5 | 3 | ✓ Full |
| JTBD-01.3 | File deleted post-download; no logging | US-2.3, US-4.2, US-4.3, US-4.4, US-4.6 | 3 | ✓ Full |
| JTBD-02.1 | Cross-browser; keyboard-only; no account | US-0.3, US-0.6, US-3.6 | 3 | ✓ Full |
| JTBD-02.2 | Privacy disclosure visible pre-upload | US-4.1, US-4.3, US-4.4, US-4.6 | 3 | ✓ Full |
| JTBD-02.3 | Scanned PDF: specific error, no blank DOCX | US-1.4, US-3.4 | 2 | ✓ Full |
| JTBD-03.1 | Tables, lists, headings preserved; zero reconstruction | US-1.1, US-1.2 | 1 | ✓ Full |
| JTBD-03.2 | Conversion ≤ 15s median; tab-independent; handles load | US-1.3, US-3.2, US-4.5 | 3 | ✓ Full |
| JTBD-03.3 | Size limit shown pre-upload; instant client rejection | US-0.4 | 2 | ✓ Full |

**All 9 JTBD outcomes are addressed by at least one story in R1.**

---

### Gap Analysis

#### Journey Stages Without Story Coverage
- **None.** All five stages (S1 Arrive, S2 Select/Upload, S3 Convert, S4 Download, S5 Error/Retry) have at least one story mapped to them.

> Note: S1 (Arrive) coverage is served by US-0.4 (size limit hint display) and the privacy disclosure behaviour owned by US-4.3 and US-4.6. US-4.3 now includes an explicit acceptance criterion requiring the plain-language privacy disclosure to be visible above the fold before any file is selected — satisfying the JTBD-02.2 hiring criterion and JRN-02.1 trust gate. See "Noted Design Gap — Resolved" below.

#### JTBD Outcomes Without Derived NaC
- **None.** All 9 JTBD outcomes have at least one NaC in the NaC Derivation Table.

#### Orphan Stories (Not Mapped to Any Journey Stage)
- **None.** All 27 stories from UserStories-PDFConverter.md appear in the Story Map Matrix.

#### Noted Design Gap — Resolved

| Gap | Resolution | Status |
|---|---|---|
| Pre-upload privacy disclosure text | A new acceptance criterion was added to **US-4.3** requiring the plain-language privacy disclosure statement to be visible above the fold and before any file is selected, without requiring scroll, click, or link navigation. This directly satisfies the JTBD-02.2 hiring criterion and JRN-02.1 trust gate. | ✓ Resolved in UserStories-PDFConverter.md |

---

## NaC-to-Acceptance Criteria Mapping

This section verifies that each NaC is consistent with (and extends or confirms) the acceptance criteria already defined in UserStories-PDFConverter.md.

| NaC-ID | NaC Statement (abbreviated) | Story | UserStory AC Alignment |
|---|---|---|---|
| NaC-01 | File picker opens without install prompt; filename and size displayed | US-0.1 | ✓ AC: "filename and human-readable file size displayed in UI"; no install check in AC — NaC makes this explicit |
| NaC-02 | Progress bar 0→100%; button spinner; no silent hang | US-0.5, US-3.1 | ✓ AC: "progress bar initialises at 0% and is immediately visible"; "updates continuously from 0% to 100%"; consistent |
| NaC-03 | job_id within 60s; text/headings/lists preserved | US-1.1 | ✓ AC: "Conversion completes within 60 seconds for PDFs up to 25 pages"; "text content, paragraph structure, headings, and lists are preserved"; fully aligned |
| NaC-04 | Download triggers immediately; full cycle ≤ 60s | US-2.1 | ✓ AC: "client issues GET /api/download/{job_id}" after success; "browser opens Save dialog without additional user interaction"; NaC adds end-to-end time bound |
| NaC-05 | Downloaded file named `{original}.docx` | US-2.2 | ✓ AC: "filename derived from original PDF filename (e.g., report.pdf → report.docx)"; fully aligned |
| NaC-06 | Green tick + "Your DOCX is ready!"; both CTA buttons visible | US-3.3 | ✓ AC: "green tick icon and message 'Your DOCX is ready!'"; "Download DOCX button"; "Convert Another File link"; fully aligned |
| NaC-07 | Server rejects invalid/oversized file before conversion | US-1.5 | ✓ AC: "server returns 400 INVALID_FILE_TYPE", "server returns 413 FILE_TOO_LARGE"; fully aligned |
| NaC-08 | Every error code → distinct user message; no raw codes | US-3.4 | ✓ AC: "every server error code maps to a distinct user-facing message"; "raw error codes, stack traces never shown"; fully aligned |
| NaC-09 | "Try Again" resets to IDLE in-place; keyboard-accessible | US-3.5 | ✓ AC: "'Try Again' resets the UI to IDLE without a full page reload"; "keyboard-focusable via Enter"; fully aligned |
| NaC-10 | Expired job_id → 404 with re-upload prompt; 202 for in-progress | US-2.4 | ✓ AC: "404 JOB_NOT_FOUND"; "202 with status 'converting'"; "user-facing message explains link has expired"; fully aligned |
| NaC-11 | Files deleted after download; UI confirms; no-store header | US-2.3, US-4.3 | ✓ AC (US-2.3): "both source and output files deleted after response sent"; AC (US-4.3): "UI confirms file is no longer stored"; "Cache-Control: no-store set"; fully aligned |
| NaC-12 | Server logs contain only job_id, duration, outcome | US-4.6 | ✓ AC: "logs do not contain file content, original filenames, or metadata"; "only job_id logged for errors"; fully aligned |
| NaC-13 | Original filename never on disk or in shell commands | US-4.2 | ✓ AC: "original uploaded filename never used as on-disk file name"; "never passed to any shell command"; fully aligned |
| NaC-14 | Inline type error in all four target browsers, no extension | US-0.3 | ✓ AC: "inline error 'Please select a PDF file.' shown immediately"; NaC extends with cross-browser scope from JTBD-02.1 |
| NaC-15 | Full cycle keyboard-only; Enter/Space on picker; logical tab order | US-0.6 | ✓ AC: "file picker activated with Enter or Space"; "logical tab order"; "visible focus indicators"; fully aligned |
| NaC-16 | aria-live announces transitions; error surfaced; icons have text | US-3.6 | ✓ AC: "state transitions announced via aria-live='polite'"; "error messages surfaced to screen readers"; "icons have accessible text"; fully aligned |
| NaC-17 | Privacy disclosure visible above fold before interaction | US-4.3, US-4.6 | ✓ Resolved — US-4.3 AC updated to explicitly require the plain-language privacy disclosure to be visible above the fold before any file is selected, without scroll or click. |
| NaC-18 | Server reads magic bytes; non-PDF rejected before write to disk | US-4.1 | ✓ AC: "reads first 8 bytes and checks for %PDF magic bytes"; "rejected with 400 before written to disk"; fully aligned |
| NaC-19 | TTL sweep deletes files >60 min; logs only count/bytes | US-4.4 | ✓ AC: "deletes temp subdirectories older than 60 minutes"; "logs only count of directories deleted and bytes freed — no content or identifying metadata"; fully aligned |
| NaC-20 | IMAGE_ONLY_PDF returned; no blank DOCX served | US-1.4 | ✓ AC: "server returns 422 IMAGE_ONLY_PDF"; "empty DOCX not served to client"; fully aligned |
| NaC-21 | IMAGE_ONLY_PDF message names scanned type + OCR alternative | US-3.4 | ✓ AC: "every error code maps to distinct user-facing message"; NaC specifies the IMAGE_ONLY_PDF message must mention scanned PDFs and name an alternative — consistent with US-3.4's error taxonomy requirement |
| NaC-22 | LibreOffice fallback transparent; both fail → 422 | US-1.2 | ✓ AC: "if pdf2docx raises exception, server invokes LibreOffice"; "fallback transparent to user"; "both fail → 422 CONVERSION_FAILED"; fully aligned |
| NaC-23 | "Converting…" spinner visible; completes tab-independent | US-3.2 | ✓ AC: "animated spinner and message 'Converting your document…'"; "state persists until response received"; NaC adds tab-independence from JTBD-03.2 |
| NaC-24 | 60s timeout terminates job; 504 returned; message suggests smaller file | US-1.3 | ✓ AC: "hard 60-second timeout"; "server returns 504 CONVERSION_TIMEOUT"; "message explains time limit exceeded and suggests smaller document"; fully aligned |
| NaC-25 | 503 SERVER_BUSY when limit reached; counter correct; message actionable | US-4.5 | ✓ AC: "server returns 503 SERVER_BUSY"; "counter incremented on acceptance, decremented on completion"; "user-facing message: 'The server is busy. Please try again in a moment.'"; fully aligned |
| NaC-26 | "Maximum file size: 50 MB" visible before any interaction | US-0.4 | ✓ AC: "maximum file size limit is communicated in the UI before the user selects a file (e.g., as a hint label)"; NaC makes placement explicit (static text, near upload control) |
| NaC-27 | Oversized file rejected ≤ 2s; error states actual size and limit | US-0.4 | ✓ AC: "files exceeding 50 MB rejected before upload begins"; "inline error 'File too large. Maximum size is 50 MB.' displayed immediately on selection"; NaC adds the 2-second timing target from JTBD-03.3 success measure |
| NaC-28 | Drop zone highlights; drop triggers same validation as picker | US-0.2 | ✓ AC: "visually designated drop zone"; "hover/highlight state"; "dropping a PDF triggers same validation as file picker"; fully aligned |

**NaC alignment summary:** 28 of 28 NaC fully aligned with acceptance criteria. NaC-17 (pre-upload privacy disclosure placement) was previously partial — resolved by adding an explicit AC to US-4.3.

---

## Summary

| Dimension | Count |
|---|---|
| Personas mapped | 3 (PER-01, PER-02, PER-03) |
| Journeys covered | 6 (JRN-01.1, JRN-01.2, JRN-02.1, JRN-02.2, JRN-03.1, JRN-03.2) |
| Journey stages | 5 (Arrive, Select/Upload, Convert, Download, Error/Retry) |
| Stories mapped | 27 of 27 (0 orphans) |
| JTBD outcomes covered | 9 of 9 |
| NaC derived | 28 |
| NaC fully aligned with AC | 27 of 28 |
| NaC partially aligned | 0 (NaC-17 resolved — see Design Gap section) |
| Releases | 1 (R1: MVP — all stories) |
| Design gaps identified | 0 (pre-upload privacy disclosure gap resolved) |

---

*Document generated: 2026-05-12 | Project: PDFConverter | Version: 1.0*
*Derived from PERSONAS-PDFConverter.md v1.0, JTBD-PDFConverter.md v1.0, JOURNEYS-PDFConverter.md v1.0, UserStories-PDFConverter.md v1.0, PRD-PDFConverter.md v1.0*
