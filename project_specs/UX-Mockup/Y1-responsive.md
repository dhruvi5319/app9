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
