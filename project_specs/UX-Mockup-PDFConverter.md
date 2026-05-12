# UX Mockup — PDFConverter

**Project:** PDF to DOCX Converter (PDFConverter)
**Generated:** 2026-05-12
**Based on:** UserStories-PDFConverter.md v1.0, PRD-PDFConverter.md v1.0, FRD-PDFConverter.md v1.0, JOURNEYS-PDFConverter.md v1.0

---

## Overview

PDFConverter is a single-page, zero-account web application. The entire user experience is contained within one URL — no navigation, no routing, no multi-page flow. The page surface is intentionally minimal: a single conversion widget centred on the screen, surrounded by just enough trust-building context (privacy statement, size limit) to unblock all three user personas before they interact.

### Design Principles

1. **Trust first, feature second.** Privacy disclosure and size limit are visible above the fold, before the upload control, because all three personas (Marcus, Priya, Dana) apply a trust filter before committing to upload.
2. **One widget, five states.** The upload area transitions through a defined state machine (`IDLE → UPLOADING → CONVERTING → SUCCESS / ERROR`). Each state replaces the previous one in-place — no page reloads, no navigation.
3. **Errors are explanations, not apologies.** Every error surface includes: what went wrong, why, and what to do next. Generic "something failed" messages are forbidden.
4. **Keyboard-first, pointer-enhanced.** Every interactive element is keyboard-reachable and operable. Drag-and-drop is an enhancement, never the only path.
5. **Silence is not acceptable feedback.** Every transition (upload start, upload progress, server processing, download trigger) has a visible and screen-reader-announced status change.

### Personas Summary

| ID | Persona | Top UX Need |
|----|---------|-------------|
| PER-01 | Marcus Webb (Office Professional) | Fast cycle, compliance-citable privacy disclosure, deletion confirmation |
| PER-02 | Priya Nair (Student / Academic) | Clear privacy statement (hard gate), full keyboard accessibility |
| PER-03 | Dana Okafor (Freelancer) | Drag-and-drop, upfront size limit, instant client-side rejection of oversized files |

### UI State Machine (Summary)

```
          Page Load
              │
              ▼
           [IDLE]
         Upload form
              │
    User selects valid PDF
              │
              ▼
       Clicks "Convert"
              │
              ▼
         [UPLOADING]
        Progress 0→100%
              │
       Upload complete
              │
              ▼
         [CONVERTING]
       Spinner + message
              │
       ┌──────┴──────┐
  Server 200       Server 4xx/5xx
       │                 │
       ▼                 ▼
    [SUCCESS]         [ERROR]
   Download +        Error msg +
  "Convert Another"  "Try Again"
       │                 │
       └────────┬────────┘
                ▼
             [IDLE]
        (in-place reset)
```

---
---

## User Flows

### Flow 00: Happy Path — Upload → Convert → Download

**Trigger:** User arrives at the page with a valid text-based PDF to convert.
**User Stories:** US-0.1, US-0.2, US-0.5, US-1.1, US-2.1, US-2.2, US-3.1, US-3.2, US-3.3
**Journeys:** JRN-01.1 (Marcus routine contract), JRN-03.1 (Dana SoW conversion)

```
[User arrives on page]
        │
        ▼
[IDLE STATE]
 Page renders with:
 • Privacy disclosure ("Your file is deleted immediately after you download it")
 • File size limit hint ("Maximum file size: 50 MB")
 • Drop zone / file picker
 • "Convert to DOCX" button [DISABLED]
        │
        ├── Via file picker: clicks button → OS dialog → selects .pdf
        │
        └── Via drag-and-drop: drags .pdf onto drop zone
                │
                ▼
        [Client-side validation passes]
         • Filename + size badge rendered ("report.pdf — 4.2 MB")
         • "Convert to DOCX" button [ENABLED]
                │
                ▼
        [User clicks "Convert to DOCX"]
                │
                ▼
        [UPLOADING STATE]
         • Button disabled + spinner on label
         • Progress bar 0% → 100% animating
         • Form locked (no new file selectable)
                │
         Upload bytes transmitted
                │
                ▼
        [CONVERTING STATE]
         • Upload form hidden
         • Animated spinner
         • "Converting your document…" message
         • (Server runs pdf2docx / LibreOffice fallback — up to 60s)
                │
         Server returns 200 + job_id
                │
                ▼
        [SUCCESS STATE]
         • Green tick icon
         • "Your DOCX is ready!" heading
         • "report.docx — 204 KB" file detail
         • [Download DOCX] button (primary CTA)
         • "File deleted from our server" confirmation line
         • "Convert another file →" link
                │
                ▼
        [Browser download triggered]
         • OS Save dialog / auto-save to Downloads
         • File: report.docx
```

**Steps:**
1. User reads privacy disclosure and size limit — no action required, trust established passively.
2. User selects PDF via picker or drag-and-drop. Filename and size appear immediately.
3. "Convert to DOCX" button activates. User clicks it.
4. Upload begins: progress bar fills from 0% to 100%.
5. Upload completes: UI switches to CONVERTING spinner with "Converting your document…"
6. Server responds 200: UI switches to SUCCESS state. Download triggers automatically via `GET /api/download/{job_id}`.
7. "Download DOCX" button also available as explicit fallback trigger.
8. "Convert another file" link resets UI to IDLE in-place.

---

### Flow 01: File Validation — Client-Side Rejection

**Trigger:** User selects or drops a file that fails client-side type or size checks.
**User Stories:** US-0.3, US-0.4, US-3.4
**Journeys:** JRN-03.2 (Dana oversized file), US-0.3 (Priya wrong type)

```
[IDLE STATE]
        │
        ├── User drops/selects NON-PDF file
        │           │
        │           ▼
        │   Inline error: "Please select a PDF file."
        │   Button remains DISABLED
        │   [User can select a different file → re-validates]
        │
        └── User drops/selects PDF > 50 MB
                    │
                    ▼
            Inline error: "Your file is 62 MB —
             maximum file size is 50 MB.
             Please reduce the file size or split
             the document and try again."
            Button remains DISABLED
            Filename + actual size shown in error for clarity
            [User can select a smaller file → re-validates]
```

**Steps:**
1. File selection triggers immediate client-side validation (type check: MIME + extension; size check: bytes vs 52,428,800).
2. Invalid file: inline error appears below the drop zone within ~100ms. Button stays disabled.
3. User selects a different file: error clears, validation re-runs on new file.
4. No bytes are transmitted to the server during client-side rejection.

---
---

### Flow 02: Server Error — Scanned PDF (Image-Only)

**Trigger:** User uploads a valid PDF that is image-only (scanned document); conversion fails with IMAGE_ONLY_PDF.
**User Stories:** US-1.4, US-3.4, US-3.5
**Journeys:** JRN-01.2 (Marcus scanned report), JRN-02.2 (Priya scanned scholarship form)

```
[IDLE] → [UPLOADING] → [CONVERTING]
                                │
                         Server returns 422
                         error code: IMAGE_ONLY_PDF
                                │
                                ▼
                         [ERROR STATE]
                          • Red alert icon
                          • "This PDF contains only images and
                             cannot be converted."
                          • Detail: "Scanned or image-based PDFs
                             require OCR, which is not supported
                             in this version. Try Adobe Acrobat or
                             Google Drive's PDF opener."
                          • [Try Again] button
                                │
                         User clicks "Try Again"
                                │
                                ▼
                         [IDLE STATE]
                          • Form re-enabled
                          • File input cleared
                          • Error message hidden
                          • Progress bar hidden
```

**Steps:**
1. Upload and conversion proceed normally — no early rejection possible client-side.
2. Server detects zero text paragraphs in output DOCX, returns 422 IMAGE_ONLY_PDF.
3. ERROR state displays: specific failure reason ("scanned image"), OCR limitation, and named alternatives (Adobe Acrobat, Google Drive).
4. "Try Again" resets to IDLE in-place. User can immediately select a different file.
5. No blank DOCX is served to the user.

---

### Flow 03: Server Error — Conversion Timeout / Failure

**Trigger:** Conversion exceeds 60-second timeout or both converters fail.
**User Stories:** US-1.2, US-1.3, US-3.4, US-3.5
**Journeys:** JRN-01.2 (Marcus recovery flow)

```
[CONVERTING]
        │
        ├── Timeout (>60s) → Server returns 504 CONVERSION_TIMEOUT
        │           │
        │           ▼
        │   [ERROR STATE]
        │    "Conversion took too long and was cancelled."
        │    Detail: "Large or complex PDFs may exceed the
        │     processing time limit. Try a smaller document."
        │    [Try Again] button
        │
        └── Both converters fail → Server returns 422 CONVERSION_FAILED
                    │
                    ▼
            [ERROR STATE]
             "We couldn't convert this PDF."
             Detail: "The document may use an unsupported format
              or structure. Try re-saving it from the source
              application."
             [Try Again] button
```

**Steps:**
1. CONVERTING spinner runs for up to 60 seconds (no frontend timeout in v1 — server enforces).
2. On timeout (504) or conversion failure (422): ERROR state shows specific message + detail.
3. Temp files are deleted server-side before error response is returned.
4. "Try Again" resets UI to IDLE.

---

### Flow 04: Network / Upload Error Recovery

**Trigger:** Network interruption during file upload.
**User Stories:** US-3.1, US-3.5
**Journeys:** Cross-journey pattern (all personas)

```
[UPLOADING]
        │
        │   Network error (XHR/fetch rejects)
        │
        ▼
[ERROR STATE]
 "Upload failed. Please check your connection and try again."
 [Try Again] button
        │
        ▼
[IDLE STATE] (on Try Again)
```

---

### Flow 05: Server Busy

**Trigger:** Server has reached MAX_CONCURRENT_JOBS limit (default: 5).
**User Stories:** US-4.5, US-3.4
**Journeys:** JRN-03.1 (Dana peak-usage risk)

```
[UPLOADING / CONVERTING]
        │
        Server returns 503 SERVER_BUSY
        │
        ▼
[ERROR STATE]
 "The server is busy. Please try again in a moment."
 Detail: "Too many files are being converted simultaneously."
 [Try Again] button
        │
        ▼
[IDLE STATE] (on Try Again — user can retry immediately)
```

---

### Flow 06: Keyboard-Only Navigation

**Trigger:** User navigates the entire upload interface without a mouse.
**User Stories:** US-0.6, US-3.6
**Journeys:** JRN-02.1 (Priya lab computer, keyboard-only)

```
[Page loads]
        │
        Tab → Privacy disclosure (read)
        Tab → File size hint (read)
        Tab → Drop zone / "Choose file" button [FOCUS RING VISIBLE]
              │
              Enter / Space → OS file picker opens
              (user navigates file picker with keyboard)
              Enter → File selected
              │
              ▼
        Tab → "Convert to DOCX" button [FOCUS RING VISIBLE] [NOW ENABLED]
              │
              Enter → Conversion begins
              │
              ▼
        [UPLOADING → CONVERTING]
        (ARIA live region announces state changes)
              │
              ▼
        [SUCCESS]
        Tab → "Download DOCX" button [FOCUS RING VISIBLE]
              │
              Enter → Download triggered
              │
        Tab → "Convert another file" link
              │
              Enter → UI resets to IDLE
```

**Steps:**
1. Tab order: privacy disclosure → size hint → file control → convert button.
2. File picker activatable via Enter or Space.
3. After file selected, Tab reaches the now-enabled Convert button.
4. All state transitions announced via `aria-live="polite"` on the status banner.
5. In SUCCESS state: "Download DOCX" button is first focusable element; "Convert another file" link follows.
6. In ERROR state: "Try Again" button is keyboard-focusable and Enter-activatable.

---
---

## Screen Designs

### Screen 00: IDLE State — Upload Page

**Purpose:** Primary entry point. Establishes trust, communicates constraints, and provides the file upload control. Must pass the "trust gate" for all three personas within 10 seconds of arrival.
**User Stories:** US-0.1, US-0.2, US-0.3, US-0.4, US-0.6, US-4.3, US-4.6
**Journeys:** JRN-01.1 (Arrive + Review Privacy), JRN-02.1 (Arrive & Scan + Read Privacy), JRN-03.1 (Open Tool + Check Size), JRN-03.2 (Assess Before Upload)

#### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    PDFConverter                              │
│              Convert PDF to Word in seconds                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  🔒 Your file is deleted from our server immediately   │  │
│  │     after you download it — we never store or log      │  │
│  │     your documents.                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                                                     │     │
│  │                                                     │     │
│  │          📄  Drag & drop your PDF here              │     │
│  │                                                     │     │
│  │               — or —                               │     │
│  │                                                     │     │
│  │          [ Choose File ]  (file picker btn)         │     │
│  │                                                     │     │
│  │          Maximum file size: 50 MB                   │     │
│  │                                                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│            [ Convert to DOCX ]  ← DISABLED                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Notes:**
- Page header is minimal: product name + one-line tagline only. No navigation menu.
- Privacy disclosure block sits **above** the drop zone — visible without scrolling on all breakpoints.
- "Maximum file size: 50 MB" displayed as static text **inside** the drop zone before any file is selected (US-0.4, Cross-Journey Pattern E).
- "Convert to DOCX" button is visually disabled (muted colour, `cursor: not-allowed`, `aria-disabled="true"`) until a valid file is selected (US-0.1).

#### After Valid File Selected (IDLE → pre-upload)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   ✓  report.pdf — 4.2 MB                           │
│      [× Clear]                                      │
│                                                     │
└─────────────────────────────────────────────────────┘

         [ Convert to DOCX ]  ← ENABLED (primary colour)
```

- Filename and human-readable size replace the drag-and-drop instructions (US-0.1 AC).
- "× Clear" link allows user to deselect and pick a different file.
- Drop zone retains its border; file icon changes to a document checkmark.

#### Drop Zone — Drag-Over State

```
┌─────────────────────────────────────────────────────┐  ← border: 2px dashed #0066CC
│                                                     │  ← background: light blue tint
│         ⬇  Drop your PDF here                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

- Activated on `dragenter` / `dragover` events (US-0.2).
- Default browser drag behaviour (`e.preventDefault()` on all drag events) disabled.

#### Client-Side Error States (within IDLE)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ⚠  wrong-document.docx                            │
│                                                     │
└─────────────────────────────────────────────────────┘
   ⚠  Please select a PDF file.
```

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  ⚠  master-contract.pdf — 62 MB                    │
│                                                     │
└─────────────────────────────────────────────────────┘
   ⚠  Your file is 62 MB — maximum file size is 50 MB.
      Please reduce the file size or split the document
      and try again.
```

- Error message appears **below** the drop zone, inline (not a modal or toast).
- Text is red; icon is ⚠ (not relying on colour alone — icon + text).
- Button remains disabled.
- Selecting a new file clears the error and re-validates (US-0.3, US-0.4).

#### Information Hierarchy

| Priority | Content | Placement |
|----------|---------|-----------|
| Primary | Drop zone / file picker (the action) | Centre, above the fold |
| Primary | Privacy disclosure | Above drop zone, always visible |
| Secondary | Size limit hint | Inside drop zone, below drag instruction |
| Secondary | Selected filename + size | Replaces drag instruction after selection |
| Tertiary | "Convert to DOCX" button label | Below drop zone |
| Tertiary | Inline validation errors | Below drop zone, red text |

#### States

| State | Drop Zone Appearance | Button State | Error Shown |
|-------|---------------------|--------------|-------------|
| Default / no file | Dashed border, drag instruction + size limit | Disabled (muted) | None |
| Drag-over (valid) | Highlighted border + tint, "Drop here" message | Disabled | None |
| File selected (valid) | Filename + size badge, checkmark icon | **Enabled** (primary) | None |
| File selected (wrong type) | Filename shown, warning icon | Disabled | "Please select a PDF file." |
| File selected (too large) | Filename + actual size shown, warning icon | Disabled | Size limit error with actual size |

#### Interactive Elements

| Element | Type | Behaviour |
|---------|------|-----------|
| Drop zone | Region + `<input type="file">` hidden | Accepts drag-drop; click delegates to hidden input |
| Choose File button | Secondary button (visible label for hidden input) | Opens OS file picker; `accept=".pdf,application/pdf"` |
| × Clear | Text link | Clears file selection, resets validation |
| Convert to DOCX | Primary CTA button | Initiates upload; disabled until valid file selected |

---
---

### Screen 01: UPLOADING State

**Purpose:** Communicates that the file is being transmitted to the server. Prevents duplicate submissions and shows real-time byte progress.
**User Stories:** US-0.5, US-3.1
**Journeys:** JRN-01.1 (Convert stage), JRN-02.1 (Convert stage), JRN-03.1 (Upload File stage)

#### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    PDFConverter                              │
│              Convert PDF to Word in seconds                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  🔒 Your file is deleted from our server immediately   │  │
│  │     after you download it — we never store or log      │  │
│  │     your documents.                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                                                     │     │
│  │   📄  report.pdf — 4.2 MB                          │     │
│  │                                                     │     │
│  │   ████████████████░░░░░░░░░░░░  58%                │     │
│  │   Uploading…                                        │     │
│  │                                                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│            [ ⟳ Uploading… ]  ← DISABLED (spinner)           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Notes:**
- Upload form is **locked**: file input disabled, drop zone not accepting new files (US-0.5 AC).
- Progress bar fills continuously from 0% to 100% based on XHR/fetch `progress` events.
- Percentage label updates alongside the bar.
- Convert button shows spinner + "Uploading…" label; remains disabled throughout upload.
- Privacy disclosure remains visible (trust continuity).

#### Information Hierarchy

| Priority | Content | Placement |
|----------|---------|-----------|
| Primary | Progress bar + percentage | Centre of the upload area |
| Primary | "Uploading…" status label | Below progress bar |
| Secondary | Filename being uploaded | Above progress bar |
| Tertiary | Disabled convert button (loading state) | Below upload area |

#### States

| State | Progress Bar | Button | Message |
|-------|-------------|--------|---------|
| Upload in progress | Animated fill 0–100% | Disabled + spinner | "Uploading…" |
| Upload complete | 100% (briefly, then transitions) | Transitions to CONVERTING | — |
| Network error | Stops at current % | Reset / transitions to ERROR | "Upload failed…" |

#### Interactive Elements

| Element | Type | Behaviour |
|---------|------|-----------|
| Progress bar | `<progress>` or styled `<div>` | Value updated by JS from XHR progress events |
| Convert button | Disabled button | Shows spinner + "Uploading…" label; not clickable |
| Drop zone | Locked region | No pointer events during upload |

---

### Screen 02: CONVERTING State

**Purpose:** Communicates that the server is processing the uploaded file. Distinct from UPLOADING — user knows all bytes are sent and conversion is underway.
**User Stories:** US-3.2
**Journeys:** JRN-01.1 (Convert stage), JRN-02.1 (Convert stage), JRN-03.1 (Convert & Wait)

#### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    PDFConverter                              │
│              Convert PDF to Word in seconds                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                                                              │
│                    ⟳  (animated spinner)                     │
│                                                              │
│              Converting your document…                       │
│                                                              │
│         report.pdf → report.docx                            │
│                                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Notes:**
- Upload form and progress bar are **hidden** (US-3.2 AC — form hidden in CONVERTING state).
- Only the spinner, status message, and filename transformation label are shown.
- No timeout countdown shown in v1 (server enforces 60s; frontend just awaits response).
- ARIA live region on status area announces "Converting your document…" when state is entered.
- Page title may update to "Converting… — PDFConverter" for tab visibility (beneficial for Dana who tabs away, JRN-03.1).

#### Information Hierarchy

| Priority | Content | Placement |
|----------|---------|-----------|
| Primary | Animated spinner | Top centre |
| Primary | "Converting your document…" | Centre |
| Secondary | Filename → output filename | Below message |

#### States

| State | Appearance | Duration |
|-------|------------|---------- |
| Converting | Spinner + message + filenames | Until server responds (up to 60s) |
| Transition to SUCCESS | Spinner fades, SUCCESS elements appear | Instant on 200 response |
| Transition to ERROR | Spinner fades, ERROR elements appear | Instant on 4xx/5xx response |

---
---

### Screen 03: SUCCESS State

**Purpose:** Confirms conversion is complete, delivers the DOCX download, and provides the deletion confirmation that Marcus (PER-01) needs for compliance and Priya (PER-02) needs for privacy confidence.
**User Stories:** US-2.1, US-2.2, US-3.3, US-4.3
**Journeys:** JRN-01.1 (Download stage), JRN-02.1 (Download stage), JRN-03.1 (Download & Quality-Check)

#### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    PDFConverter                              │
│              Convert PDF to Word in seconds                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    ✓  (green tick icon)                      │
│                                                              │
│                  Your DOCX is ready!                         │
│                                                              │
│          report.docx  ·  204 KB                             │
│                                                              │
│           [ ↓ Download DOCX ]  ← PRIMARY BUTTON             │
│                                                              │
│   🗑  Your file has been deleted from our server.            │
│                                                              │
│         ─────────────────────────────────                   │
│         Convert another file →                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Notes:**
- Green tick icon is large and prominent — visual confirmation distinct from progress/error states.
- "Your DOCX is ready!" heading uses green colour for success state (US-3.3 AC — colour-coded green).
- Output filename (`report.docx`) is derived from original PDF name per US-2.2.
- File size shown (`204 KB`) confirms download completeness.
- **Automatic download:** On entering SUCCESS state, browser JS immediately calls `GET /api/download/{job_id}` (US-2.1). The "Download DOCX" button is a fallback for users whose browser blocked the automatic download.
- **Deletion confirmation line** ("Your file has been deleted from our server") is a distinct inline statement — not buried in the privacy disclosure. This satisfies Marcus's compliance need (JRN-01.1 Delight Opportunity) and Priya's privacy confidence (US-4.3 AC).
- "Convert another file →" link resets UI to IDLE state in-place without page reload (US-3.3 AC).
- The icon has an accessible text alternative (`aria-label="Success"` or equivalent).

#### Information Hierarchy

| Priority | Content | Placement |
|----------|---------|-----------|
| Primary | Green tick + "Your DOCX is ready!" | Top centre |
| Primary | Download DOCX button | Centre, prominent |
| Secondary | Output filename + size | Above button |
| Secondary | Deletion confirmation | Below button, icon-prefixed |
| Tertiary | "Convert another file" link | Bottom of panel |

#### States

| State | Appearance | Notes |
|-------|------------|-------|
| Success (initial) | Green tick, auto-download fires, Download button visible | Auto-download triggered on state entry |
| Success (download triggered) | Same view; OS download dialog open | UI does not change |
| Success (user clicks Download again) | Server returns 404 JOB_NOT_FOUND → ERROR state | Files already deleted after first download |

#### Interactive Elements

| Element | Type | Behaviour |
|---------|------|-----------|
| Download DOCX button | Primary CTA | Issues `GET /api/download/{job_id}`; forces browser download |
| Convert another file | Text link | Resets UI to IDLE in-place; clears file selection |

---
---

### Screen 04: ERROR State

**Purpose:** Communicates what went wrong, why, and what to do next — specific enough that users resolve the situation in under 30 seconds (JRN-01.2 / JRN-02.2 design target).
**User Stories:** US-3.4, US-3.5, US-3.6
**Journeys:** JRN-01.2 (See Error + Retry), JRN-02.2 (See Specific Error), JRN-03.2 (See Instant Rejection)

#### Layout (Generic Error)

```
┌──────────────────────────────────────────────────────────────┐
│                    PDFConverter                              │
│              Convert PDF to Word in seconds                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    ⚠  (red alert icon)                       │
│                                                              │
│        [PRIMARY ERROR MESSAGE — plain language]              │
│                                                              │
│        [Secondary detail line — smaller, lighter text]       │
│                                                              │
│              [ Try Again ]  ← PRIMARY BUTTON                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

#### Error Message Variants

Each error code maps to a specific primary message + secondary detail. No raw codes, stack traces, or internal details are shown (US-3.4 AC).

```
IMAGE_ONLY_PDF:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  This PDF contains only images and cannot be converted.  │
│                                                              │
│      Scanned or image-based PDFs require OCR, which is not  │
│      supported in this version. Try Adobe Acrobat or        │
│      Google Drive's PDF opener.                             │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

CONVERSION_TIMEOUT:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  Conversion took too long and was cancelled.             │
│                                                              │
│      Large or complex PDFs may exceed the processing time   │
│      limit. Try a smaller document.                         │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

CONVERSION_FAILED:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  We couldn't convert this PDF.                           │
│                                                              │
│      The document may use an unsupported format or          │
│      structure. Try re-saving it from the source            │
│      application.                                           │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

FILE_TOO_LARGE (server-side, post-upload):
┌─────────────────────────────────────────────────────────────┐
│   ⚠  Your file is too large to convert.                      │
│                                                              │
│      Maximum file size is 50 MB. Please try a smaller PDF.  │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

INVALID_FILE_TYPE (server-side):
┌─────────────────────────────────────────────────────────────┐
│   ⚠  This file doesn't appear to be a valid PDF.             │
│                                                              │
│      The server was unable to verify the file as a PDF      │
│      document.                                              │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

SERVER_BUSY:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  The server is busy. Please try again in a moment.       │
│                                                              │
│      Too many files are being converted simultaneously.     │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

Upload network error:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  Upload failed. Please check your connection and        │
│      try again.                                             │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

JOB_NOT_FOUND (expired download link):
┌─────────────────────────────────────────────────────────────┐
│   ⚠  Your conversion result has expired.                     │
│                                                              │
│      The download link is no longer valid. Please convert   │
│      the file again.                                        │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘

INTERNAL_ERROR / unmapped:
┌─────────────────────────────────────────────────────────────┐
│   ⚠  Something went wrong on our end.                        │
│                                                              │
│      An unexpected server error occurred. Please try again. │
│                                                              │
│                    [ Try Again ]                             │
└─────────────────────────────────────────────────────────────┘
```

#### Information Hierarchy

| Priority | Content | Placement |
|----------|---------|-----------|
| Primary | Red alert icon + primary error message | Top centre, large text |
| Secondary | Error detail / next step suggestion | Below primary, smaller text |
| Primary | "Try Again" button | Below detail, primary colour |

#### States

| State | Appearance | User Action |
|-------|------------|-------------|
| ERROR (any code) | Red icon + primary message + detail + Try Again button | Click "Try Again" or use keyboard Enter |
| After "Try Again" | UI resets to IDLE; error cleared; file input cleared | User can immediately select a new file |

#### Interactive Elements

| Element | Type | Behaviour |
|---------|------|-----------|
| Try Again button | Primary CTA | Resets to IDLE: clears error, clears file input, hides progress bar, re-enables form |

#### Error State Notes

- Red is used as the status colour AND an alert icon is shown — colour alone never carries the meaning (US-3.6, accessibility requirement).
- Error messages arrive via ARIA live region (`aria-live="assertive"` for errors to announce immediately) (US-3.6 AC).
- "Try Again" button receives focus automatically when ERROR state is entered (keyboard user doesn't need to Tab to find it).
- No full page reload occurs on "Try Again" — the UI is reset in JavaScript (US-3.5 AC).

---
---

## Interaction Patterns

### Pattern 01: In-Place State Replacement

**When to use:** Every UI state transition (IDLE → UPLOADING → CONVERTING → SUCCESS/ERROR → IDLE).
**Behaviour:** The content area of the upload widget is replaced in-place using JavaScript DOM manipulation. No page navigation, no `window.location` changes, no history push. The browser URL stays the same throughout.
**Why:** Preserves user context; eliminates the need to re-navigate after errors or completions. All three personas benefit: Marcus avoids losing context mid-workflow (JRN-01.2), Priya doesn't lose keyboard focus position unexpectedly (JRN-02.1), Dana avoids extra steps in a time-pressured workflow (JRN-03.1).
**Examples:** CONVERTING spinner replacing UPLOADING progress bar; SUCCESS panel replacing CONVERTING spinner; IDLE form replacing ERROR state on "Try Again".

---

### Pattern 02: Progressive Disclosure of File Metadata

**When to use:** After a file is selected (IDLE state).
**Behaviour:** Before file selection: drop zone shows generic instruction + size limit. After valid file selected: instructions are replaced by filename + human-readable file size badge. After invalid file selected: filename is shown alongside an error indicator.
**Why:** Reduces cognitive load on page load (no file metadata to show yet); surfaces relevant feedback at the moment it's useful.
**Examples:** "report.pdf — 4.2 MB" replacing "Drag & drop your PDF here" after file selection.

---

### Pattern 03: Dual-Mode File Input

**When to use:** File selection (IDLE state only).
**Behaviour:** A visually prominent drop zone region and a clearly labelled "Choose File" button both trigger the same file selection + validation logic. The drop zone handles `dragenter`, `dragover`, `dragleave`, and `drop` events. The button activates a hidden `<input type="file">`. Both paths call the same `handleFileSelect(file)` function.
**Why:** Dana prefers drag-and-drop for desktop efficiency (JRN-03.1); Priya and Marcus use the file picker on restricted/unfamiliar machines. Neither path requires additional steps.
**Examples:** Drop zone highlights on drag-over; file picker button always visible for pointer-free or accessibility-first scenarios.

---

### Pattern 04: Locked Form During Upload

**When to use:** UPLOADING state.
**Behaviour:** The file input and drop zone are disabled (`pointer-events: none`, `aria-disabled="true"`) while upload is in progress. The "Convert" button shows a spinner and "Uploading…" label. No new file can be selected until the upload resolves (success, error, or network failure).
**Why:** Prevents accidental double submissions and race conditions where a new file selection could interrupt the in-flight upload.
**Examples:** Drop zone ignores drag events during upload; file input refuses click events.

---

### Pattern 05: Automatic Download + Explicit Button Fallback

**When to use:** SUCCESS state entry.
**Behaviour:** On entering SUCCESS state, JavaScript immediately initiates `GET /api/download/{job_id}` which triggers the browser's file download mechanism (via `Content-Disposition: attachment`). A "Download DOCX" button is also rendered and triggers the same endpoint on click — for browsers that block automatic downloads or users who dismiss the OS dialog.
**Why:** US-2.1 requires both automatic triggering and an explicit button. The automatic trigger is the fast path for Marcus and Dana; the button is the safety net.
**Caution:** A second click of "Download DOCX" after files have been deleted will return 404 JOB_NOT_FOUND → transitions to ERROR state with "Your conversion result has expired." message.

---

### Pattern 06: Client-Side Validation Before Server Contact

**When to use:** File selection (IDLE state).
**Behaviour:** Validation runs synchronously in the browser on `change` (file picker) and `drop` (drag-and-drop) events. Checks: (1) MIME type (`file.type === "application/pdf"`), (2) extension (`file.name.toLowerCase().endsWith('.pdf')`), (3) size (`file.size <= 52428800`). All three checks must pass before the Convert button enables. No bytes are sent to the server unless all three pass.
**Why:** Immediate feedback (< 100ms) vs. waiting for a server round-trip. Dana's oversized file rejection scenario (JRN-03.2) requires this: "within 2 seconds of file selection."
**Note:** Client-side validation is a UX guard, not a security boundary. The server independently validates all three conditions server-side (US-4.1).

---

### Pattern 07: Error → IDLE Reset via "Try Again"

**When to use:** ERROR state.
**Behaviour:** "Try Again" button click (or Enter keypress when focused) executes: (1) hide error panel, (2) clear file input (`input.value = ''`), (3) reset progress bar to 0%, (4) re-render IDLE state upload form, (5) focus the file input / Choose File button.
**Why:** Full in-place reset with auto-focus means keyboard users immediately land on the next actionable element without additional Tab presses. Dana and Marcus both benefit from zero navigation overhead in their retry workflows.

---

### Pattern 08: ARIA Live Region Announcements

**When to use:** All state transitions.
**Behaviour:** A visually hidden `<div aria-live="polite" aria-atomic="true" id="status-announcer">` element is updated with a text description on every state change:
- UPLOADING: "Uploading report.pdf — 0%"
- UPLOADING progress: "Uploading — 58%"  
- CONVERTING: "Converting your document. Please wait."
- SUCCESS: "Conversion complete. Your DOCX is ready to download."
- ERROR: Updated with `aria-live="assertive"` and error message text.

Error announcements use `assertive` (interrupts screen reader) rather than `polite` (waits for idle) to surface failures immediately (US-3.6 AC).

---
---

## Responsive Considerations

The application is a single-widget page. The layout adjusts to ensure the upload widget remains fully usable at all breakpoints without horizontal scrolling or truncated content.

### Desktop (> 1024px)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PDFConverter                                │
│                   Convert PDF to Word in seconds                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│           ┌──────────────────────────────────────────┐             │
│           │  🔒 Privacy disclosure — single line      │             │
│           └──────────────────────────────────────────┘             │
│                                                                     │
│           ┌──────────────────────────────────────────┐             │
│           │                                          │             │
│           │   Drag & drop area — generous height     │             │
│           │                                          │             │
│           └──────────────────────────────────────────┘             │
│                                                                     │
│                  [ Convert to DOCX ]                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

- Widget max-width: ~600px, horizontally centred.
- Drop zone minimum height: 200px — sufficient drag target.
- Privacy disclosure is a single pill/banner above the drop zone.
- All text readable at default browser zoom (16px base).

---

### Tablet (768px – 1024px)

```
┌──────────────────────────────────────────────────┐
│                  PDFConverter                    │
│           Convert PDF to Word in seconds         │
├──────────────────────────────────────────────────┤
│                                                  │
│   ┌────────────────────────────────────────┐     │
│   │  🔒 Privacy disclosure (2 lines ok)    │     │
│   └────────────────────────────────────────┘     │
│                                                  │
│   ┌────────────────────────────────────────┐     │
│   │  Drag & drop / Choose File             │     │
│   │  Maximum file size: 50 MB              │     │
│   └────────────────────────────────────────┘     │
│                                                  │
│          [ Convert to DOCX ]                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

- Widget fills ~90% of viewport width.
- Drop zone height: 160px minimum.
- Privacy disclosure wraps to 2 lines if needed — remains above the drop zone.
- Touch target size: all buttons and links ≥ 44 × 44px (WCAG 2.5.5 AA).

---

### Mobile (< 768px)

```
┌────────────────────────────────────┐
│           PDFConverter             │
│   Convert PDF to Word in seconds   │
├────────────────────────────────────┤
│                                    │
│  ┌──────────────────────────────┐  │
│  │  🔒 Privacy disclosure       │  │
│  │     (2–3 lines)              │  │
│  └──────────────────────────────┘  │
│                                    │
│  ┌──────────────────────────────┐  │
│  │                              │  │
│  │  [ Choose File ]             │  │
│  │  (drag-and-drop hidden on    │  │
│  │   touch-only devices)        │  │
│  │                              │  │
│  │  Maximum file size: 50 MB    │  │
│  └──────────────────────────────┘  │
│                                    │
│  [ Convert to DOCX ]  ← full width │
│                                    │
└────────────────────────────────────┘
```

- Widget fills 100% of viewport width with `16px` horizontal padding.
- Drag-and-drop zone: Still rendered but drag instruction text changes to "Tap to choose a file" since most mobile users won't drag. Drag events still handled if a capable browser sends them.
- "Convert to DOCX" button is full-width on mobile for easy tap target.
- Progress bar fills full width.
- Error messages wrap fully — no truncation.
- SUCCESS state: "Download DOCX" button is full-width.

---

### Breakpoint Summary

| Breakpoint | Widget Width | Drop Zone Height | Button Width |
|------------|-------------|-----------------|-------------|
| Desktop > 1024px | max 600px, centred | 200px | auto (fits content) |
| Tablet 768–1024px | 90% viewport | 160px | auto |
| Mobile < 768px | 100% – 32px | 120px | 100% |

### Universal Layout Rules

- No horizontal scrollbar at any breakpoint.
- Privacy disclosure always above the fold (no scrolling needed to see it).
- Size limit hint always visible inside the drop zone before file selection.
- Error messages always visible without scrolling in their inline position.
- Font size minimum: 14px for body text; 16px for button labels and error messages.

---
---

## Accessibility Notes

All accessibility requirements are derived from US-0.6 (keyboard-accessible upload interface) and US-3.6 (screen reader accessibility for state changes). Target conformance: **WCAG 2.1 Level AA**.

### Colour Contrast

| Element | Foreground | Background | Min Ratio | Notes |
|---------|-----------|-----------|-----------|-------|
| Body text | #1A1A1A | #FFFFFF | 4.5:1 | Normal text |
| Button label (primary) | #FFFFFF | #0057D8 (blue) | 4.5:1 | Convert, Download buttons |
| Button label (disabled) | #767676 | #E0E0E0 | 4.5:1 | Must still meet contrast |
| Success message heading | #1A5C2A | #FFFFFF | 4.5:1 | "Your DOCX is ready!" |
| Error message heading | #9B1C1C | #FFFFFF | 4.5:1 | Error state primary message |
| Error detail text | #6B2222 | #FFFFFF | 4.5:1 | Secondary error line |
| Progress bar fill | #0057D8 | #E8F0FE | 3:1 | UI component (WCAG 1.4.11) |
| Drop zone border (default) | #767676 | #FFFFFF | 3:1 | UI component |
| Drop zone border (drag-over) | #0057D8 | #EBF2FF | 3:1 | UI component |

**Rule:** Colour is never the **only** means of conveying information:
- Success state: green colour + ✓ tick icon + "Your DOCX is ready!" text.
- Error state: red colour + ⚠ alert icon + error message text.
- Progress: percentage label accompanies the bar fill.
- Disabled button: muted colour + `aria-disabled="true"` + `cursor: not-allowed`.

---

### Keyboard Navigation

**Tab order (IDLE state):**
1. Page heading (if focusable / landmark)
2. Privacy disclosure (informational — skip-link not required, but readable)
3. Drop zone / "Choose File" button
4. "Convert to DOCX" button (disabled until valid file selected)

**Tab order (SUCCESS state):**
1. "Download DOCX" button (auto-focused on state entry)
2. "Convert another file" link

**Tab order (ERROR state):**
1. "Try Again" button (auto-focused on state entry)

**Key bindings:**
- `Enter` / `Space` on "Choose File" button → opens OS file picker
- `Enter` on "Convert to DOCX" button → initiates upload (when enabled)
- `Enter` on "Download DOCX" button → triggers download
- `Enter` on "Convert another file" link → resets to IDLE
- `Enter` on "Try Again" button → resets to IDLE
- `Tab` / `Shift+Tab` → moves focus forward/backward through all interactive elements

**Focus indicators:**
- All interactive elements display a visible focus outline (minimum: 2px solid, offset 2px).
- Focus ring colour: `#0057D8` (distinguishable from both the white background and element backgrounds).
- Focus indicators must be visible in both light mode and any OS high-contrast mode.

**Focus management on state transitions:**
- IDLE → UPLOADING: focus remains on (now-disabled) Convert button.
- UPLOADING → CONVERTING: focus moves to the status spinner region (focusable landmark).
- CONVERTING → SUCCESS: focus moves to "Download DOCX" button (auto-focus).
- CONVERTING / UPLOADING → ERROR: focus moves to "Try Again" button (auto-focus).
- ERROR → IDLE (Try Again): focus moves to "Choose File" button.

---

### Screen Reader Considerations

**Semantic HTML:**
- Page uses a single `<main>` landmark containing the upload widget.
- All headings use proper `<h1>` / `<h2>` hierarchy (page title = `<h1>`, state headings = `<h2>`).
- The drop zone is a `<div>` with `role="region"` and `aria-label="File upload area"`.
- The file input has an associated `<label>` element (visually styled as the "Choose File" button).

**Form labelling:**
```html
<label for="file-input" class="choose-file-button">Choose File</label>
<input id="file-input" type="file" accept=".pdf,application/pdf" />
```

**Button states:**
- Disabled button uses `aria-disabled="true"` (not `disabled` attribute alone, which removes it from tab order) so keyboard users can reach it and understand why it can't be activated.
- Active spinner button: `aria-label="Converting — please wait"`.

**Live regions:**
```html
<!-- Polite: progress announcements -->
<div id="status-live" aria-live="polite" aria-atomic="true" class="sr-only">
  <!-- Updated by JS on state changes -->
</div>

<!-- Assertive: error announcements (interrupt screen reader immediately) -->
<div id="error-live" aria-live="assertive" aria-atomic="true" class="sr-only">
  <!-- Updated by JS on error state entry -->
</div>
```

**Icon accessibility:**
- ✓ tick: `<span aria-hidden="true">✓</span><span class="sr-only">Success:</span>`
- ⚠ alert: `<span aria-hidden="true">⚠</span><span class="sr-only">Error:</span>`
- ⟳ spinner: `<span role="img" aria-label="Loading"></span>`
- 🔒 privacy icon: `<span aria-hidden="true">🔒</span>` (decorative — text carries the meaning)

**Progress bar:**
```html
<progress id="upload-progress" 
          value="58" 
          max="100" 
          aria-label="Upload progress"
          aria-valuetext="58 percent uploaded">
</progress>
```

**State change announcements (examples):**
- On UPLOADING: `status-live.textContent = "Uploading report.pdf…"`
- On CONVERTING: `status-live.textContent = "Conversion in progress. Please wait."`
- On SUCCESS: `status-live.textContent = "Conversion complete. Your DOCX is ready to download."`
- On ERROR: `error-live.textContent = "Error: This PDF contains only images and cannot be converted."`

---

### Additional Notes

- **No motion-dependent feedback:** The progress bar includes a percentage label. Users with `prefers-reduced-motion` will see a static bar fill without animation; functionality unchanged.
- **No time-based interactions:** No CAPTCHA, no countdown timers that require user action, no auto-dismissing alerts.
- **No reliance on hover states for critical information:** Filename/size, privacy disclosure, size limit, error messages, and button labels are all visible without hover.
- **Touch target sizes:** All buttons and links ≥ 44 × 44px to satisfy WCAG 2.5.5 (AAA) and Apple HIG / Material guidance for mobile usability.

---
