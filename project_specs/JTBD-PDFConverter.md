# Jobs-to-be-Done Document
# PDF to DOCX Converter (PDFConverter)

| Field | Value |
|---|---|
| **Product Name** | PDFConverter |
| **Document Version** | 1.0 |
| **Date** | 2026-05-11 |
| **Status** | Draft |
| **Related Personas** | PERSONAS-PDFConverter.md v1.0 (PER-01, PER-02, PER-03) |
| **Related PRD** | PRD-PDFConverter.md v1.0 |
| **Derived From** | PRD Sections 2, 5, 6, 7; Persona goals, pain points, top tasks |

---

## JTBD Summary Table

| JTBD-ID | Persona | Job Statement (abbreviated) | Priority |
|---|---|---|---|
| JTBD-01.1 | PER-01 Marcus Webb | Get a received PDF into editable Word format instantly, without installing software or creating an account | P0 |
| JTBD-01.2 | PER-01 Marcus Webb | Understand exactly what went wrong when a conversion fails so I can act on it without guessing | P0 |
| JTBD-01.3 | PER-01 Marcus Webb | Trust that a confidential document I uploaded is gone from the server the moment I have my DOCX | P0 |
| JTBD-02.1 | PER-02 Priya Nair | Convert a PDF form into an editable DOCX on any browser I happen to be using, with no account required | P0 |
| JTBD-02.2 | PER-02 Priya Nair | Verify the tool's privacy behavior before uploading so I feel safe sharing personal or academic work | P0 |
| JTBD-02.3 | PER-02 Priya Nair | Receive a clear, plain-language explanation when a scanned PDF cannot be converted, so I can find an alternative | P0 |
| JTBD-03.1 | PER-03 Dana Okafor | Receive a DOCX that faithfully preserves the tables, lists, and headings from a client PDF so I don't lose billable time to manual reformatting | P0 |
| JTBD-03.2 | PER-03 Dana Okafor | Complete the full upload-to-download cycle fast enough that conversion doesn't break my work rhythm | P0 |
| JTBD-03.3 | PER-03 Dana Okafor | Know a file's size limits before I start uploading so I can make a go/no-go decision upfront, not after a failed attempt | P0 |

---

## PER-01: Marcus Webb — Office Professional

### JTBD-01.1: Zero-Friction Conversion of Professional Documents

**Job Statement:**
When I receive a vendor contract or internal report that needs redlining and I'm at my corporate laptop with no admin rights, I want to upload the PDF and download a ready-to-edit DOCX in a single browser session, so I can begin editing in Word without installing software, creating an account, or involving IT.

**Current Alternatives:**
- Emails the PDF to a personal account and uses a consumer converter at home — introduces a privacy risk and a delay
- Asks a colleague with Adobe Acrobat access to convert and send back — adds latency and a dependency
- Copies text manually from Adobe Reader into a Word document — loses all formatting, takes 20–30 minutes

**Hiring Criteria:**
- Works entirely in-browser with no extension, plugin, or software installation required
- No account creation or email address at any point in the workflow
- File picker or drag-and-drop upload accepts PDF files up to at least 50 MB
- Converted DOCX retains heading hierarchy, paragraph structure, and list formatting without manual cleanup for standard text-based documents
- Full cycle (upload → convert → download) completes in under 60 seconds

**Success Measure:** Marcus completes an upload → convert → download cycle in under 60 seconds, and the resulting DOCX requires no structural reformatting before he can begin redlining.

**Related Features:** F0, F1, F2, F3
**Priority:** P0

---

### JTBD-01.2: Actionable Error Recovery Without Starting Over

**Job Statement:**
When a conversion attempt fails mid-workflow, I want to receive an explicit message that identifies the specific reason for the failure and tells me what to do next, so I can recover immediately without refreshing the page, losing my place, or guessing at a fix.

**Current Alternatives:**
- Refreshes the page and re-uploads the same file hoping for a different result — wastes time, rarely works
- Abandons the tool and tries a different online converter from scratch — loses 5–10 minutes per failed attempt
- Sends the document to IT with a vague description — creates a support ticket with multi-day turnaround

**Hiring Criteria:**
- Error messages identify the failure mode by name (e.g., "File too large — maximum is 50 MB", "File type not supported", "Conversion timed out")
- Error state includes a retry action that re-initializes the upload form without a full page reload
- No silent failures — every conversion outcome (success or failure) triggers visible UI feedback
- If the file is image-only/scanned, the error explicitly says so (even though OCR is out of scope)

**Success Measure:** Marcus can read an error message, understand the cause, and decide on his next action (retry, adjust file, use a different tool) within 30 seconds of the failure notification appearing.

**Related Features:** F3, F0
**Priority:** P0

---

### JTBD-01.3: Verified File Deletion for Compliance Confidence

**Job Statement:**
When I upload a confidential vendor contract or internal report that is subject to my firm's data handling policies, I want clear confirmation that the file is deleted from the server as soon as I download my DOCX, so I can use the tool without violating compliance obligations or worrying about unauthorized data retention.

**Current Alternatives:**
- Reviews terms of service of each online converter before using — slow, terms are rarely clear, often ambiguous on retention
- Routes all sensitive documents through IT-approved tools only — Adobe Acrobat, which requires a license he doesn't have
- Avoids online converters entirely for confidential documents, manually re-types content — painful and error-prone

**Hiring Criteria:**
- UI messaging explicitly states that files are deleted after download (plain language, not legal boilerplate)
- No logged file metadata, document content, or filenames that could identify the user or document
- Temporary file TTL cleanup ensures files are not left on the server even if the download is interrupted
- Privacy policy or in-UI disclosure is concise and specific — "files deleted immediately after download"

**Success Measure:** Marcus can articulate to a compliance colleague exactly what happens to uploaded files (deleted after download, not stored, not logged) based solely on information the UI provides — without reading external documentation.

**Related Features:** F4, F2
**Priority:** P0

---

## PER-02: Priya Nair — Student / Academic

### JTBD-02.1: Cross-Browser Conversion With No Account or Installation

**Job Statement:**
When I need to fill in or modify a PDF form for a scholarship application or university submission and I'm working on whichever computer is available — my MacBook at home or a lab PC at university — I want to convert the PDF to DOCX using whatever browser is installed, so I can type into the document in Word or Google Docs without paying for software or creating an account.

**Current Alternatives:**
- Uses Adobe Acrobat's free tier online — hits paywalls for editing features after basic conversion
- Tries Google Drive's built-in PDF opening — loses form structure, fields become un-fillable text blocks
- Types all content manually into a new Word document — loses original formatting, takes 30+ minutes for complex forms

**Hiring Criteria:**
- Works in current versions of Safari, Chrome, Firefox, and Edge with no browser extension required
- No account, email address, or personal information required at any point
- No subscription, payment prompt, or upsell interruption during or after conversion
- UI is fully keyboard-navigable (file upload, submit, download) for shared lab computers without mice
- Conversion completes and file downloads correctly across all four target browsers

**Success Measure:** Priya completes a full conversion on a university lab computer running Chrome, using keyboard navigation only, with no account prompt, in under 60 seconds.

**Related Features:** F0, F1, F2, F3
**Priority:** P0

---

### JTBD-02.2: Privacy Assurance Before Uploading Sensitive Documents

**Job Statement:**
When I am about to upload a document that contains my academic work, personal details, or scholarship materials, I want to see clear, plain-language confirmation of what the tool does with my file before I click upload, so I can make an informed decision about whether this tool is safe to trust — and proceed with confidence if it is.

**Current Alternatives:**
- Reads the full terms of service of each online converter before uploading — time-consuming, terms are often vague on retention
- Uses only university-approved tools even when they lack the needed feature — limits her options significantly
- Converts a test PDF first to see whether the tool behaves acceptably, then re-uploads the real file — doubles the effort

**Hiring Criteria:**
- A concise privacy disclosure is visible on the upload page before any interaction — not buried in a footer or a modal
- Disclosure uses plain language: what happens to the file, when it is deleted, what is not stored
- No ad network tracking scripts that would suggest file data could be shared with third parties
- Behavior matches the disclosure: no observable persistence of files after download (verified by server-side deletion)
- No email capture field or opt-in checkbox appears during the workflow

**Success Measure:** Priya reads the privacy disclosure in under 30 seconds and decides to proceed — without opening an external privacy policy link or asking a third party whether the tool is safe.

**Related Features:** F4, F3
**Priority:** P0

---

### JTBD-02.3: Explicit Failure Explanation for Scanned PDFs

**Job Statement:**
When I upload a PDF that turns out to be a scanned image rather than a text-based document, I want to receive a specific, plain-language error message that explains why the conversion produced no usable output, so I can immediately understand the limitation and look for an alternative solution rather than wondering if I did something wrong.

**Current Alternatives:**
- Downloads a blank or near-blank DOCX, assumes the tool failed, and retries — wastes 5–10 minutes before giving up
- Posts in a student forum asking if others have successfully converted the same PDF — slow, uncertain
- Manually transcribes the scanned content into Word — works but takes hours for multi-page documents

**Hiring Criteria:**
- When an image-only PDF is uploaded, the system returns a specific error (not a generic "conversion failed") that mentions the scanned/image-only nature of the document
- Error message suggests a concrete next step (e.g., "This PDF appears to be a scanned image. OCR is not supported — try a tool that offers OCR conversion")
- Error appears within the normal conversion feedback flow — same location, same timing as other errors
- No blank DOCX is served as a "success" when the output contains no usable text

**Success Measure:** When Priya uploads a scanned PDF, she reads the error message and understands within 15 seconds that the issue is the PDF type (not a tool bug), and knows what to do next.

**Related Features:** F3, F1
**Priority:** P0

---

## PER-03: Dana Okafor — Freelancer / Small Business Owner

### JTBD-03.1: Formatting-Faithful Conversion That Eliminates Manual Reconstruction

**Job Statement:**
When I receive a client PDF containing a statement of work, rate table, or reference contract that I need to adapt, I want to download a DOCX where the tables, numbered lists, and heading structure are intact and accurate, so I can start editing client deliverables immediately without spending 20–30 minutes reconstructing the document layout.

**Current Alternatives:**
- Uses a paid online converter — pays per-conversion or monthly, acceptable if output is reliable, but current tools still mangle complex tables
- Opens the PDF in Adobe Acrobat and manually re-creates the table structure in Word — reliable but consumes 30+ minutes per document
- Copies PDF text into Word and re-applies all formatting manually — fastest fallback but destroys any table relationship

**Hiring Criteria:**
- Table structures (rows, columns, cell content) are preserved in the output DOCX — not collapsed into plain text
- Numbered and bulleted lists retain their hierarchy and numbering scheme
- Heading styles are applied in the output DOCX at the correct level (H1, H2, H3) matching the source PDF
- Output quality is consistent across repeated conversions of the same file (no random degradation)
- For straightforward client documents (standard SoW, contract, rate table), zero manual layout reconstruction is required

**Definition — "standard document" for this job:** A single-column, text-primary document created in a standard authoring tool (Microsoft Word, Google Docs, LibreOffice) and exported or printed to PDF. Includes: statements of work, contracts, rate tables with simple grids (≤ 5 columns), and numbered clause documents. Excludes: scanned PDFs, multi-column magazine layouts, heavily nested tables (tables inside table cells), PDFs with embedded forms, PDFs with custom font subsets or ligatures that are not encoded as Unicode.

**Success Measure:** Dana opens the converted DOCX and can begin editing content within 2 minutes of download — with no table rows to merge, no list numbering to restore, and no heading styles to manually reapply — for any PDF that qualifies as a "standard document" per the definition above.

**Related Features:** F1, F2, F3
**Priority:** P0

---

### JTBD-03.2: Fast End-to-End Conversion That Fits a Billable Workflow

**Job Statement:**
When I need to convert a client PDF between tasks in my working day, I want the full upload-to-download cycle to complete in under 30 seconds so that the conversion step is invisible to my workflow — a brief pause, not a productivity interruption.

**Current Alternatives:**
- Uses a desktop tool (LibreOffice headless) — fast but requires a local setup she'd rather not maintain
- Batches conversions at the start of the day before billing hours — works but requires planning ahead and forfeits on-demand use
- Accepts 60–90 second waits from current online tools — tolerable for occasional use, frustrating at semi-frequent cadence

**Hiring Criteria:**
- Median conversion time ≤ 15 seconds for PDFs under 10 pages (matching PRD NFR performance target)
- Upload progress indicator confirms that large files are transmitting and not stalled
- "Converting…" status indicator confirms the server is working — no silent wait with no feedback
- Conversion completes without requiring Dana to stay on the tab or keep the browser in focus

**Success Measure:** For a typical 5–8 page client PDF, Dana sees the download prompt within 15 seconds of clicking "Convert" — measured from click to download-ready state.

**Related Features:** F0, F1, F2, F3
**Priority:** P0

---

### JTBD-03.3: Upfront File Size Transparency to Avoid Wasted Upload Attempts

**Job Statement:**
When I'm about to upload a large client PDF — a 40-page SoW or multi-section reference contract — I want to see the file size limit clearly displayed before I begin uploading, so I can make an informed go/no-go decision upfront rather than discovering the limit after a failed multi-minute upload.

**Current Alternatives:**
- Attempts the upload and waits for an error response — wastes 3–5 minutes on large files before learning the limit
- Checks the tool's FAQ or help page for size limits — rarely documented clearly, often requires a separate page visit
- Compresses the PDF in advance to get under an unknown limit — guesswork, may degrade document quality

**Hiring Criteria:**
- Maximum file size limit is displayed prominently on the upload interface — visible before the user selects a file
- Client-side file size validation fires immediately after file selection — not after upload begins
- Error message for an oversized file identifies the limit and the actual file size ("Your file is 62 MB — maximum is 50 MB")
- Size limit validation is consistent between client-side display and server-side enforcement

**Success Measure:** Dana sees the 50 MB size limit before selecting a file, and — if her file exceeds the limit — receives the rejection within 2 seconds of file selection (before any upload begins), with a message that states both the limit and her file's actual size.

**Related Features:** F0, F4, F3
**Priority:** P0

---

## Outcome-to-Feature Traceability

| JTBD-ID | Related Feature(s) | Expected Outcome |
|---|---|---|
| JTBD-01.1 | F0, F1, F2, F3 | Office professional completes upload → convert → download in under 60 seconds, no account, no install |
| JTBD-01.2 | F3, F0 | Error state surfaces the failure reason and a retry action; user recovers within 30 seconds |
| JTBD-01.3 | F4, F2 | UI confirms immediate file deletion post-download; no logged metadata; TTL cleanup as safety net |
| JTBD-02.1 | F0, F1, F2, F3 | Conversion completes on any current browser; keyboard-only navigation works end-to-end |
| JTBD-02.2 | F4, F3 | Plain-language privacy disclosure visible pre-upload; no email capture; no third-party ad tracking |
| JTBD-02.3 | F3, F1 | Scanned PDF triggers specific error with next-step guidance; no blank DOCX served as success |
| JTBD-03.1 | F1, F2, F3 | Tables, numbered lists, and heading hierarchy intact in output DOCX; zero manual layout reconstruction for standard docs |
| JTBD-03.2 | F0, F1, F2, F3 | Median conversion time ≤ 15 seconds for PDFs under 10 pages; progress feedback visible throughout |
| JTBD-03.3 | F0, F4, F3 | File size limit shown pre-upload; client-side rejection fires within 2 seconds of file selection |

---

## NaC Preview

*Candidate Natural Acceptance Criteria — to be refined in STORY-MAP*

| JTBD-ID | Outcome | Candidate Natural Acceptance Criterion |
|---|---|---|
| JTBD-01.1 | Full cycle under 60 seconds, no account | Given a standard text-based PDF, when a user selects the file and clicks "Convert to DOCX", then the DOCX is available for download within 60 seconds and no login or account prompt appears at any stage |
| JTBD-01.1 | Formatting preserved for standard documents | Given a PDF with headings, paragraphs, and numbered lists, when conversion completes, then the downloaded DOCX retains the heading hierarchy and list structure without manual reformatting |
| JTBD-01.2 | Specific, actionable error message | Given a file that exceeds the size limit, when the user attempts upload, then an error message names the limit, the file's actual size, and presents a retry option — without a page reload |
| JTBD-01.2 | Retry without losing context | Given a failed conversion, when the user clicks retry, then the upload form resets without a full page navigation and the user can select a new file immediately |
| JTBD-01.3 | File deletion confirmed in UI | Given a successful download, when the download completes, then the UI displays a confirmation that the file has been deleted from the server |
| JTBD-01.3 | No file persistence after download | Given any completed or failed conversion, when 60 minutes have elapsed, then no uploaded or converted file remains in the server's temp directory |
| JTBD-02.1 | Works on all target browsers | Given a user on Safari, Chrome, Firefox, or Edge (current − 1), when they complete the full conversion workflow, then the DOCX downloads correctly with no browser-specific errors |
| JTBD-02.1 | Fully keyboard-navigable | Given a user with no mouse, when they tab through the interface and press Enter/Space to trigger upload and download, then all steps complete successfully using keyboard only |
| JTBD-02.2 | Privacy disclosure visible pre-upload | Given a first-time visitor on the upload page, when they view the page before interacting, then a plain-language statement about file deletion is visible without scrolling or clicking |
| JTBD-02.2 | No email capture in workflow | Given any stage of the conversion workflow, when a user progresses from upload to download, then no email field, opt-in checkbox, or account creation prompt appears |
| JTBD-02.3 | Scanned PDF error is specific | Given a PDF consisting entirely of scanned images, when conversion completes, then the user sees an error message that explicitly identifies the document as image-only and explains that OCR is not supported |
| JTBD-02.3 | No blank DOCX on scanned PDF | Given a scanned image-only PDF, when conversion is attempted, then no downloadable DOCX is produced — only the specific error message is shown |
| JTBD-03.1 | Tables preserved in output | Given a PDF with a multi-column table, when conversion completes, then the downloaded DOCX contains the same table with rows, columns, and cell content intact |
| JTBD-03.1 | Numbered lists preserved | Given a PDF with a numbered list, when conversion completes, then the DOCX retains the list numbering scheme without collapsing to plain text |
| JTBD-03.2 | Median conversion ≤ 15 seconds | Given a text-based PDF of 10 pages or fewer, when conversion is triggered, then the download prompt appears within 15 seconds (median across 10 test runs) |
| JTBD-03.2 | Progress feedback throughout | Given any conversion in progress, when the server is processing, then a "Converting…" indicator is visible and the user is not presented with a blank or frozen screen |
| JTBD-03.3 | Size limit shown pre-upload | Given a user who has not yet selected a file, when they view the upload interface, then the maximum file size limit is displayed as static text near the upload control |
| JTBD-03.3 | Client-side rejection within 2 seconds | Given a file exceeding 50 MB, when the user selects it via the file picker, then a size-limit error appears within 2 seconds — before any upload transmission begins — and states the limit and the file's actual size |

---

*Document generated: 2026-05-11 | Project: PDFConverter | Version: 1.0*
*Derived from PERSONAS-PDFConverter.md v1.0 and PRD-PDFConverter.md v1.0*
