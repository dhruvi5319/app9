# User Journey Maps
# PDF to DOCX Converter (PDFConverter)

| Field | Value |
|---|---|
| **Product Name** | PDFConverter |
| **Document Version** | 1.0 |
| **Date** | 2026-05-12 |
| **Status** | Draft |
| **Related Personas** | PERSONAS-PDFConverter.md v1.0 (PER-01, PER-02, PER-03) |
| **Related JTBD** | JTBD-PDFConverter.md v1.0 |
| **Related PRD** | PRD-PDFConverter.md v1.0 |

---

## Journey Index

| JRN-ID | Persona | Scenario | Key JTBD(s) | Stages |
|---|---|---|---|---|
| JRN-01.1 | PER-01 Marcus Webb | Routine vendor contract conversion at work | JTBD-01.1, JTBD-01.3 | 5 |
| JRN-01.2 | PER-01 Marcus Webb | Conversion fails — recover without losing context | JTBD-01.2 | 5 |
| JRN-02.1 | PER-02 Priya Nair | First-time use: privacy check then form conversion | JTBD-02.2, JTBD-02.1 | 6 |
| JRN-02.2 | PER-02 Priya Nair | Uploads a scanned PDF — receives explicit failure guidance | JTBD-02.3 | 5 |
| JRN-03.1 | PER-03 Dana Okafor | Client SoW conversion embedded in billable workflow | JTBD-03.1, JTBD-03.2 | 5 |
| JRN-03.2 | PER-03 Dana Okafor | Oversized PDF — size limit decision before upload begins | JTBD-03.3 | 4 |

---

## PER-01: Marcus Webb — Office Professional

---

### JRN-01.1: Routine Vendor Contract Conversion at Work

**Persona:** PER-01 (Marcus Webb)

**Scenario:** Marcus has just received a vendor contract PDF via email that he needs to redline and return by end of day. He has no admin rights on his corporate laptop and can't install desktop software. He navigates to PDFConverter in his browser, uploads the contract, and expects a clean DOCX back in under a minute so he can get straight to editing in Word.

**Related Jobs:** JTBD-01.1, JTBD-01.3

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Arrive | Opens PDFConverter URL in a new browser tab; scans the page | Upload page (F0) | "Is this going to ask me to sign up? Let me check." | Cautiously neutral | Conditioned wariness from past tools that gate access behind sign-up | Immediately visible "no account required" message + plain-language privacy disclosure reassures him before he reads further |
| Review Privacy | Reads the file deletion notice near the upload control | Privacy disclosure (F4, F3) | "Okay — it says files are deleted after download. That's what I need to tell compliance." | Relieved, trust building | Unclear or buried disclosures in other tools have cost him time in the past | Plain-language statement ("Your file is deleted immediately after you download it") visible above the fold with no link to chase |
| Select File | Uses file picker to locate the vendor contract PDF on his desktop | File upload control (F0) | "50 MB limit — my file is 4 MB, fine." | Focused | None at this stage — limit is visible and his file is well within it | Client-side size display on file selection confirms the file is accepted before upload starts |
| Convert | Clicks "Convert to DOCX"; watches upload progress then "Converting…" indicator | Progress indicator, status messages (F3, F1) | "It's doing something — good. How long will this take?" | Attentive, slightly impatient | Previous tools gave no feedback during processing — he couldn't tell if they'd frozen | Animated "Converting…" state with estimated time or a simple elapsed counter reduces perceived wait |
| Download | Download prompt appears; clicks to save; sees "File deleted from server" confirmation | Download button, deletion confirmation (F2, F4, F3) | "Good — one click, file saved. And it confirms deletion. I can tell compliance this is clean." | Satisfied, confident | No current tool gives him a post-download deletion confirmation he can cite | Inline deletion confirmation ("Your file has been deleted from our server") appears after download — no extra step required |

### Key Moments
- **Trust Gate:** Arrive stage — Marcus decides within 10 seconds whether to proceed or close the tab; failure to show privacy info immediately loses him
- **Decision Point:** Review Privacy — he silently applies a compliance filter; missing or vague disclosure = abandonment
- **Delight Opportunity:** Download stage — deletion confirmation is unexpected and memorable; Marcus may cite it to colleagues as evidence of trustworthiness

### Success Outcome
Marcus completes the upload → convert → download cycle in under 60 seconds, receives a DOCX with intact headings and paragraph structure, and can confirm to a compliance colleague that files are deleted immediately after download — all from UI-visible information (JTBD-01.1, JTBD-01.3 success measures).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Arrive | F0 (File Upload Interface) |
| Review Privacy | F4 (File Security & Privacy Controls), F3 (User Feedback & Status) |
| Select File | F0 (File Upload Interface) |
| Convert | F1 (Server-Side Conversion), F3 (User Feedback & Status) |
| Download | F2 (DOCX File Download), F4 (File Security & Privacy Controls), F3 (User Feedback & Status) |

---

### JRN-01.2: Conversion Fails — Recover Without Losing Context

**Persona:** PER-01 (Marcus Webb)

**Scenario:** Marcus uploads a scanned PDF report that a partner firm sent as an image-only document. The conversion fails. Marcus needs to understand what went wrong within seconds, decide his next step, and either retry with a different file or move to an alternative — all without refreshing the page or starting over from scratch.

**Related Jobs:** JTBD-01.2

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Upload | Selects and uploads the scanned report PDF; sees progress indicator complete | File upload control, progress indicator (F0, F3) | "File uploaded fine — should be converting now." | Expectant | None yet — the upload itself succeeded | Clear upload completion state distinguishes upload success from conversion success |
| Wait | Watches "Converting…" indicator for several seconds | Status indicator (F3, F1) | "Taking a bit longer than I'd expect for a 6-page document…" | Slightly anxious | No estimated time makes waits feel longer than they are | Progress feedback with a soft timeout cue ("still working…") reduces anxiety during longer jobs |
| See Error | Error message appears: "This PDF appears to be a scanned image. PDFConverter can't extract text from image-based documents. Try a tool that supports OCR." | Error state (F3) | "Okay — it's a scanned image. That's why it failed. I need an OCR tool." | Surprised, then quickly oriented | Other tools either return a blank DOCX silently or show a generic "conversion failed" message with no explanation | Specific, plain-language error with failure reason (scanned/image-only) and a suggested next step gives Marcus an immediate decision path |
| Assess Options | Reads the suggested next step; decides to forward the PDF to a colleague with OCR access | Error state, retry button (F3) | "I can't fix this here — I'll send it to Sarah who has Adobe. At least I know why." | Resigned but not frustrated | Without a clear error, he'd waste time re-uploading, testing file settings, or escalating to IT | "Try a tool with OCR" guidance surfaces in the error message itself — no external search needed to understand the limitation |
| Retry with New File | Clicks "Try another file" to reset the upload form; selects a different (text-based) PDF | Retry button, file upload control (F0, F3) | "Let me try the other report — that one should be a real text PDF." | Re-engaged, calm | Full page reload on other tools loses his previous context | In-place form reset (no page navigation) lets Marcus immediately re-upload a different file without re-navigating |

### Key Moments
- **Critical Moment:** See Error stage — the quality of the error message determines whether Marcus understands what happened (and recovers in 30 seconds) or wastes 5–10 minutes guessing
- **Risk of Abandonment:** Wait stage — if the spinner runs too long with no feedback, Marcus may assume the tool is broken and close the tab before the error even appears
- **Delight Opportunity:** Retry stage — a seamless in-place retry (no page reload) creates a noticeably better experience than any competing tool Marcus has used

### Success Outcome
Marcus reads the error message, understands the failure cause (scanned PDF), and decides his next action within 30 seconds of the error appearing — without refreshing the page or escalating to IT (JTBD-01.2 success measure).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Upload | F0 (File Upload Interface), F3 (User Feedback & Status) |
| Wait | F1 (Server-Side Conversion), F3 (User Feedback & Status) |
| See Error | F3 (User Feedback & Status) |
| Assess Options | F3 (User Feedback & Status) |
| Retry with New File | F0 (File Upload Interface), F3 (User Feedback & Status) |

---

## PER-02: Priya Nair — Student / Academic

---

### JRN-02.1: First-Time Use — Privacy Check Then Form Conversion

**Persona:** PER-02 (Priya Nair)

**Scenario:** Priya needs to complete a scholarship application that arrived as a PDF form. She's on a university lab computer running Chrome. She has never used PDFConverter before and reads the upload page carefully before committing to upload — her document contains personal details and she will not use a tool she doesn't trust. Once satisfied, she completes the conversion using keyboard navigation only (the lab computers don't always have mice available).

**Related Jobs:** JTBD-02.2, JTBD-02.1

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Arrive & Scan | Lands on the upload page; reads it top-to-bottom before interacting | Upload page (F0, F4) | "No sign-up? Good. Let me find what it says about my file." | Cautious, evaluative | Most tools bury privacy info in footers or lengthy ToS documents — she's been burned before | Page leads with a brief, scannable privacy disclosure in the main content area — not a footer link |
| Read Privacy Disclosure | Locates and reads the file deletion statement; checks for ad scripts / tracking indicators | Privacy disclosure (F4, F3) | "Files deleted after download, no logging — that's exactly what I need. No ads visible either." | Increasingly trusting | Tools with ad networks make her suspicious that file data is shared with third parties | Plain-language disclosure with specific, verifiable language ("deleted immediately after download, never stored or logged") builds confidence; clean, ad-free UI reinforces it |
| Select File (Keyboard) | Tabs to the file upload button; presses Enter to open file picker; navigates to the scholarship form PDF | File upload control — keyboard nav (F0) | "Tab… Enter… okay, file picker opened. Now I need to find the file." | Focused, methodical | Lab computers often lack reliable mouse access; upload controls that aren't keyboard-focusable block her | Upload control is fully keyboard-operable — tab-focusable with Enter/Space activation; visible focus indicator shows which element is active |
| Convert | Presses Tab to "Convert to DOCX" button; presses Enter to trigger conversion; follows status messages | Convert button, status indicators (F1, F3) | "Uploading… now converting… it's still going. It hasn't frozen, right?" | Attentive, slightly anxious | Slow or feedback-free conversion states on lab machines feel like crashes | "Converting…" status indicator confirms activity; Priya doesn't need to keep focus on the tab for conversion to complete |
| Download (Keyboard) | Tabs to the "Download DOCX" button; presses Enter; file saves to Downloads | Download button — keyboard nav (F2, F3) | "Download prompt… Enter to save. That worked. Let me check the file opens in Google Docs." | Relieved, satisfied | Download triggers that require mouse interaction exclude keyboard-only users | Download button is keyboard-focusable; browser Save dialog responds to keyboard; confirmation message appears on screen |
| Verify | Opens the downloaded DOCX in Google Docs; checks that form fields are present and editable | Google Docs (outside product scope) | "Form structure looks intact — I can type into the fields. Good." | Confident | If structure is lost, she has to manually recreate the form — 30+ minutes of work | Accurate conversion output (preserved form layout) is the ultimate payoff; post-download deletion confirmation reinforces trust on first use |

### Key Moments
- **Trust Gate (Hard Block):** Read Privacy Disclosure — Priya will not proceed if she cannot find a clear, specific, non-legalese privacy statement; this is a binary go/no-go decision
- **Accessibility Critical Path:** Select File and Download stages — keyboard navigation failure at either point means complete task failure; no workaround available in a mouseless lab environment
- **Delight Opportunity:** Arrive & Scan — a clean, ad-free page with an immediately visible privacy statement is a powerful differentiator for Priya's persona; she will remember and recommend it

### Success Outcome
Priya reads the privacy disclosure in under 30 seconds, proceeds to upload using keyboard-only navigation on Chrome, and downloads a usable DOCX without any account prompt, ad interruption, or accessibility barrier (JTBD-02.2 and JTBD-02.1 success measures).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Arrive & Scan | F0 (File Upload Interface), F4 (File Security & Privacy Controls) |
| Read Privacy Disclosure | F4 (File Security & Privacy Controls), F3 (User Feedback & Status) |
| Select File (Keyboard) | F0 (File Upload Interface) |
| Convert | F1 (Server-Side Conversion), F3 (User Feedback & Status) |
| Download (Keyboard) | F2 (DOCX File Download), F3 (User Feedback & Status) |
| Verify | F2 (DOCX File Download) |

---

### JRN-02.2: Scanned PDF Upload — Explicit Failure Guidance

**Persona:** PER-02 (Priya Nair)

**Scenario:** Priya receives a scanned PDF of an old scholarship application form from her advisor — the document was physically printed, filled in, and scanned. She uploads it to PDFConverter expecting a DOCX she can edit. The conversion cannot extract text because the PDF is image-only. Priya needs to understand exactly why it failed — not receive a blank file or a generic error — so she knows to look for an OCR tool rather than assuming she did something wrong.

**Related Jobs:** JTBD-02.3

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Select & Upload | Selects the scanned PDF and clicks "Convert to DOCX" | File upload control, progress indicator (F0, F3) | "Okay, uploading… the file size looks fine. Should work." | Expectant, neutral | No way to know before upload that the PDF is image-only — client-side detection is not feasible | Upload accepts the file normally; no false rejection creates unnecessary confusion |
| Wait | Watches "Converting…" indicator; conversion completes but produces no usable output | Status indicator (F1, F3) | "Still converting… a bit slow for a short document." | Slightly uncertain | Image-only PDFs may be detected quickly by the library, but feedback timing feels the same as a real conversion | Library-level detection of image-only PDFs can return early with a specific signal — minimizing wait before the error appears |
| See Specific Error | Error appears: "This PDF appears to be a scanned image. We can only convert text-based PDFs — scanned documents require OCR, which isn't supported here. Try an OCR tool like Adobe Acrobat or Google Drive's PDF opener." | Error message (F3) | "Oh — it's a scanned image. That's why. It's not the tool breaking, it's the file type. I need an OCR tool." | Surprised, then quickly clear-headed | Generic "conversion failed" errors from other tools led her to waste 10 minutes retrying and posting in a forum | Error message names the specific problem (scanned/image-only), explains the limitation (no OCR in v1), and names concrete alternatives — all in one message |
| Decide Next Step | Reads the suggested alternatives; decides to try Google Drive's PDF import | Error state, external tool (F3, outside scope) | "Google Drive might handle this — let me try. At least I know exactly what I'm dealing with." | Oriented, purposeful | Without a clear next step, she'd spend time searching or guessing | Named next-step suggestions (Google Drive, Adobe Acrobat) make the path forward concrete and immediate |
| Retry or Leave | Clicks "Try another file" to confirm the in-place reset is available; decides to leave since she needs OCR | Retry button (F0, F3) | "Nothing else to convert right now — I'll come back when I have a text PDF." | Calm, no frustration | Frustration risk is low when the cause is clear and blame is correctly attributed to the file, not the tool | Clean exit path: Priya leaves without frustration, remembering PDFConverter as the tool that told her the truth |

### Key Moments
- **Critical Moment:** See Specific Error — the difference between a specific, blaming-the-right-thing error and a generic failure message determines whether Priya spends 2 minutes or 30 minutes resolving the situation
- **Risk of Abandonment (Wrong Reason):** If a blank DOCX is served instead of an error, Priya may blame herself or the tool incorrectly and never return — even though PDFConverter works fine for text PDFs
- **Trust Signal:** A clear, honest error that correctly explains the limitation (OCR out of scope) actually builds trust — honesty about what the tool can't do reinforces credibility for what it can

### Success Outcome
Priya reads the error message within 15 seconds of it appearing and correctly understands that the limitation is the scanned PDF format (not a tool bug), and knows to seek an OCR tool — no blank DOCX is served (JTBD-02.3 success measure).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Select & Upload | F0 (File Upload Interface), F3 (User Feedback & Status) |
| Wait | F1 (Server-Side Conversion), F3 (User Feedback & Status) |
| See Specific Error | F3 (User Feedback & Status) |
| Decide Next Step | F3 (User Feedback & Status) |
| Retry or Leave | F0 (File Upload Interface), F3 (User Feedback & Status) |

---

## PER-03: Dana Okafor — Freelancer / Small Business Owner

---

### JRN-03.1: Client SoW Conversion Embedded in Billable Workflow

**Persona:** PER-03 (Dana Okafor)

**Scenario:** Dana has received a 7-page Statement of Work PDF from a new client. She needs to adapt it into her own contract template — which means the tables, numbered clauses, and heading hierarchy must survive conversion intact. She has a 30-minute window between two billable calls and needs the conversion to complete fast enough that it doesn't eat into client time. She uses PDFConverter as her go-to converter and runs the workflow in a familiar rhythm.

**Related Jobs:** JTBD-03.1, JTBD-03.2

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Open Tool | Navigates to PDFConverter tab (already bookmarked); glances at the interface | Upload page (F0) | "Same interface — good. Let me just get this uploaded." | Efficient, task-focused | Context switching to a new tool layout costs mental energy | Consistent, unchanged UI rewards returning users; no new onboarding friction |
| Check Size | Notices the 50 MB limit displayed before selecting a file; mentally confirms her 7-page SoW is well under | Size limit display (F0, F4) | "50 MB — that 7-pager is maybe 2 MB. Fine." | Confident, ready | Other tools don't show limits until after a failed upload | Prominent pre-upload size display eliminates one cognitive step from Dana's go/no-go assessment |
| Upload File | Drags and drops the SoW PDF onto the upload area; watches upload progress bar | Drag-and-drop, progress bar (F0, F3) | "Uploading fast — it's a small file." | Efficient | None — drag-and-drop is her preferred method for desktop files | Drag-and-drop UX removes the file picker navigation step; progress bar confirms transmission in real time |
| Convert & Wait | "Converting…" indicator runs for ~10 seconds; Dana moves to another tab briefly | Status indicator (F1, F3) | "I'll check my email while this runs — should be done in a sec." | Calm, multitasking | Tools that require her to stay on the page to trigger the download break her multitasking habit | Conversion completes and download is available whether or not Dana is on the tab; no focus-dependent behavior |
| Download & Quality-Check | Download triggers automatically; Dana opens the DOCX in Word; scans headings, table structure, and clause numbering | DOCX download (F2, F3), Word (external) | "Table looks intact. Clause numbering — 1, 2, 3 — good. H1 and H2 styles applied. This is clean." | Satisfied, relieved | Free converters routinely collapse tables to plain text, forcing 20–30 minute manual reconstruction | High-quality conversion output (tables, lists, headings preserved) is the core differentiator for Dana; zero reconstruction = direct billable time saved |

### Key Moments
- **Decision Point:** Quality-Check stage — Dana opens the DOCX and makes a binary judgment within 60 seconds: "edit-ready" or "needs reconstruction." A failed quality check means she switches to a paid competitor immediately
- **Delight Opportunity:** Convert & Wait — being able to tab away and return to a ready download (rather than babysitting the page) signals that PDFConverter respects her time
- **Recurring Value Confirmation:** Every successful cycle reinforces habit formation; Dana's workflow embedding is the key to retention

### Success Outcome
Dana's 7-page SoW DOCX is download-ready within 15 seconds of clicking "Convert," with tables, numbered clauses, and heading styles fully intact — requiring zero manual layout reconstruction before she begins editing (JTBD-03.1 and JTBD-03.2 success measures).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Open Tool | F0 (File Upload Interface) |
| Check Size | F0 (File Upload Interface), F4 (File Security & Privacy Controls) |
| Upload File | F0 (File Upload Interface), F3 (User Feedback & Status) |
| Convert & Wait | F1 (Server-Side Conversion), F3 (User Feedback & Status) |
| Download & Quality-Check | F2 (DOCX File Download), F3 (User Feedback & Status) |

---

### JRN-03.2: Oversized PDF — Size Limit Decision Before Upload Begins

**Persona:** PER-03 (Dana Okafor)

**Scenario:** Dana receives a 52-page reference contract PDF from a client — a comprehensive master services agreement she needs to adapt. Before dragging the file to the upload area, she checks whether the tool can handle it. She sees the 50 MB limit clearly displayed. She selects the file anyway to see its actual size, and PDFConverter immediately rejects it client-side with the file's size and the limit stated explicitly. Dana can now make an informed decision: compress the PDF, split it, or use a different tool — without having wasted time on a multi-minute upload.

**Related Jobs:** JTBD-03.3

### Journey Stages

| Stage | Action | Touchpoint | Thinking | Feeling | Pain Point | Opportunity |
|---|---|---|---|---|---|---|
| Assess Before Upload | Lands on upload page; reads the file size limit before selecting anything | Size limit display (F0, F4) | "50 MB — this thing is 52 pages. Probably under the limit, but let me check." | Calculating, methodical | Other tools don't show limits; she's been burned by a 5-minute upload that failed at the end | Upfront size limit display (static text near the upload control) enables go/no-go assessment before any action |
| Select Oversized File | Uses file picker to select the 62 MB contract PDF | File upload control (F0) | "Selected… wait, is it going to reject this? Let's see." | Curious, slightly braced | Without client-side validation, she'd watch a progress bar for minutes before discovering the problem | Client-side size validation fires within 2 seconds of file selection — before any upload bytes are transmitted |
| See Instant Rejection | Error appears immediately: "Your file is 62 MB — maximum file size is 50 MB. Please reduce the file size or split the document and try again." | Client-side error (F0, F3) | "62 MB — over the limit. Okay. I need to compress this or split it." | Mildly frustrated (at the file, not the tool), but oriented | The tool gave her the information she needed immediately; no upload time wasted | Specific error states both the file's actual size and the limit — no guessing or comparison required; concrete next steps ("compress or split") give her an immediate path forward |
| Decide & Act | Closes the file picker; opens her PDF in a compression tool; reduces file to 44 MB; returns to PDFConverter | File compression tool (external), upload page (F0) | "44 MB — that should be under. Let me retry." | Purposeful, pragmatic | Other tools make her guess whether compression will get her under the limit | Knowing the exact limit (50 MB) lets Dana target a specific compression threshold with confidence |

### Key Moments
- **Critical Prevention:** Select Oversized File — instant client-side rejection is the entire value of this journey; a 2-second response vs. a 5-minute failed upload is a material time saving for Dana
- **Decision Point:** Decide & Act — the specificity of the error (62 MB vs. 50 MB limit) enables Dana to choose between compression and splitting with accurate information, not guesswork
- **Trust Signal:** A tool that immediately and honestly rejects a file (rather than silently failing mid-upload) earns professional credibility with Dana's "reliability-first" evaluation criteria

### Success Outcome
Dana sees the 50 MB size limit before selecting a file, receives the client-side rejection within 2 seconds of file selection (before any upload begins), reads both her file's actual size (62 MB) and the limit (50 MB), and can immediately decide how to proceed — with no upload time wasted (JTBD-03.3 success measure).

### Feature Touchpoints

| Stage | Features |
|---|---|
| Assess Before Upload | F0 (File Upload Interface), F4 (File Security & Privacy Controls) |
| Select Oversized File | F0 (File Upload Interface) |
| See Instant Rejection | F0 (File Upload Interface), F3 (User Feedback & Status) |
| Decide & Act | F0 (File Upload Interface) |

---

## Cross-Journey Patterns

### Pattern A: Privacy Disclosure as a Pre-Condition for Action

**Appears in:** JRN-01.1 (Marcus), JRN-02.1 (Priya), JRN-02.2 (Priya implicit)

All three personas scan for privacy/data handling information before interacting with the upload control. The trust gate is earlier for PER-02 (Priya) — it's a hard block — but PER-01 (Marcus) applies a softer compliance filter at the same stage. **Opportunity:** A single, prominently placed, plain-language disclosure ("Your file is deleted from our server immediately after you download it — we never store or log your documents") addresses all three personas with one design decision.

---

### Pattern B: Error Message Quality Determines Recovery Time

**Appears in:** JRN-01.2 (scanned PDF error), JRN-02.2 (scanned PDF error), JRN-03.2 (oversized file error)

All three personas hit error states across multiple journeys. In each case, the difference between a specific error (names the cause + next step) and a generic error ("conversion failed") is the difference between 15–30 seconds of recovery time and 5–30 minutes of guessing, retrying, and forum-searching. **Opportunity:** A single error taxonomy (scanned image, file too large, unsupported type, timeout) with templated specific messages and retry actions solves this across all personas simultaneously.

---

### Pattern C: Upload Progress Feedback Reduces Anxiety

**Appears in:** JRN-01.1 (Marcus), JRN-02.1 (Priya), JRN-03.1 (Dana)

All three personas pass through a "wait" stage where no visible change occurs during conversion. For Marcus and Priya, this creates low-grade anxiety ("Has it frozen?"). For Dana, it's tolerable only because she tabs away. **Opportunity:** A visually distinct, animated "Converting…" indicator — separate from the upload progress bar — eliminates ambiguity about whether the system is working. Estimated time or elapsed counter amplifies the benefit for all three personas.

---

### Pattern D: In-Place Retry Preserves Workflow Continuity

**Appears in:** JRN-01.2 (Marcus retry after failure), JRN-02.2 (Priya optional retry), JRN-03.2 (Dana retry after rejection)

All three personas benefit from being able to re-upload a corrected file without navigating away or refreshing the page. For Marcus (corporate context), a page reload risks losing the conversion context. For Dana (billable time), any extra step has a cost. **Opportunity:** A single "Try another file" button that resets the upload form in-place (no page navigation) is a universal solution shared across all three personas and four journeys.

---

### Pattern E: File Size Limit Visibility Prevents Wasted Effort

**Appears in:** JRN-01.1 (Marcus — confirms he's under limit), JRN-03.1 (Dana — routine check), JRN-03.2 (Dana — primary scenario)

Displaying the file size limit before file selection is a low-cost design decision that benefits all personas, but is critical for PER-03 (Dana) who regularly handles large client documents. **Opportunity:** Static text "Maximum file size: 50 MB" displayed near the upload control — visible without interaction — costs nothing to implement and eliminates an entire failure mode for Dana's highest-frequency workflow.

---

## Journey-to-JTBD Traceability

| JRN-ID | Stage | JTBD-ID | Expected Outcome |
|---|---|---|---|
| JRN-01.1 | Arrive | JTBD-01.1 | User sees no sign-up requirement; proceeds immediately |
| JRN-01.1 | Review Privacy | JTBD-01.3 | User reads plain-language deletion statement; compliance question answered |
| JRN-01.1 | Select File | JTBD-01.1 | Client-side size validation fires; file accepted without upload delay |
| JRN-01.1 | Convert | JTBD-01.1 | Conversion completes within 60 seconds; animated status confirms activity |
| JRN-01.1 | Download | JTBD-01.1, JTBD-01.3 | DOCX downloads; deletion confirmation appears; full cycle ≤ 60 seconds |
| JRN-01.2 | Upload | JTBD-01.2 | Upload progress visible; upload success distinguished from conversion success |
| JRN-01.2 | Wait | JTBD-01.2 | "Converting…" indicator confirms activity; timeout handled gracefully |
| JRN-01.2 | See Error | JTBD-01.2 | Specific error names failure cause (scanned image); next step provided |
| JRN-01.2 | Assess Options | JTBD-01.2 | User understands cause within 30 seconds; can decide next action immediately |
| JRN-01.2 | Retry with New File | JTBD-01.2 | In-place form reset; no page reload required to re-upload |
| JRN-02.1 | Arrive & Scan | JTBD-02.2 | Privacy disclosure visible above fold; no sign-up prompt encountered |
| JRN-02.1 | Read Privacy Disclosure | JTBD-02.2 | User reads and approves disclosure in < 30 seconds; no external link needed |
| JRN-02.1 | Select File (Keyboard) | JTBD-02.1 | Upload control is keyboard-focusable and operable with Enter/Space |
| JRN-02.1 | Convert | JTBD-02.1 | Conversion completes in target browser (Chrome); status feedback visible |
| JRN-02.1 | Download (Keyboard) | JTBD-02.1 | Download button keyboard-operable; file saves successfully via keyboard |
| JRN-02.1 | Verify | JTBD-02.1 | Converted DOCX opens and is editable in Google Docs; form structure intact |
| JRN-02.2 | Select & Upload | JTBD-02.3 | Upload proceeds normally; no pre-upload false rejection of image PDF |
| JRN-02.2 | Wait | JTBD-02.3 | Conversion library detects image-only PDF; returns early with specific signal |
| JRN-02.2 | See Specific Error | JTBD-02.3 | Error names scanned/image-only type; explains OCR not supported; suggests alternatives |
| JRN-02.2 | Decide Next Step | JTBD-02.3 | User correctly attributes failure to file type (not tool bug) within 15 seconds |
| JRN-02.2 | Retry or Leave | JTBD-02.3 | No blank DOCX served; in-place retry available; user exits without frustration |
| JRN-03.1 | Open Tool | JTBD-03.2 | Familiar UI; no re-orientation friction for returning user |
| JRN-03.1 | Check Size | JTBD-03.3 | Size limit visible pre-upload; user confirms go/no-go before file selection |
| JRN-03.1 | Upload File | JTBD-03.2 | Drag-and-drop accepted; upload progress bar visible; fast for small files |
| JRN-03.1 | Convert & Wait | JTBD-03.2 | Conversion completes ≤ 15 seconds (median for ≤ 10-page PDF); tab-independent |
| JRN-03.1 | Download & Quality-Check | JTBD-03.1, JTBD-03.2 | Tables, lists, headings intact; zero manual reconstruction; download ≤ 15 seconds |
| JRN-03.2 | Assess Before Upload | JTBD-03.3 | Size limit displayed as static text before file selection |
| JRN-03.2 | Select Oversized File | JTBD-03.3 | Client-side validation fires within 2 seconds of file selection; no bytes transmitted |
| JRN-03.2 | See Instant Rejection | JTBD-03.3 | Error states exact file size and limit; concrete next steps ("compress or split") provided |
| JRN-03.2 | Decide & Act | JTBD-03.3 | User has exact size information; can target compression threshold with confidence |

---

*Document generated: 2026-05-12 | Project: PDFConverter | Version: 1.0*
*Derived from PERSONAS-PDFConverter.md v1.0, JTBD-PDFConverter.md v1.0, PRD-PDFConverter.md v1.0*
