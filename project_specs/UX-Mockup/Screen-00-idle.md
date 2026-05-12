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
