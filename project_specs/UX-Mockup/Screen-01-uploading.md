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
