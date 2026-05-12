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
