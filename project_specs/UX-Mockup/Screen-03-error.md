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
