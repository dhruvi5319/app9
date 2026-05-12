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
