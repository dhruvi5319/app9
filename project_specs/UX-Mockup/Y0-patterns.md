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
