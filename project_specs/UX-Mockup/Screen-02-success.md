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
