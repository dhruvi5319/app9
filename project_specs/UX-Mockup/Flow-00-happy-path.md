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
