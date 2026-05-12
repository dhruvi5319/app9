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
