# Persona Profiles
# PDF to DOCX Converter (PDFConverter)

| Field | Value |
|---|---|
| **Product Name** | PDFConverter |
| **Document Version** | 1.0 |
| **Date** | 2026-05-11 |
| **Status** | Draft |
| **Related PRD** | PRD-PDFConverter.md v1.0 |
| **Derived From** | PRD Section 2 (Problem Statement), Section 2.2 (Target Users), Section 5 (Features), Section 7 (Success Metrics) |

---

## Persona Summary Table

| PER-ID | Name | Role | Primary Goal |
|---|---|---|---|
| PER-01 | Marcus Webb | Office Professional | Convert received PDFs into editable Word documents quickly, without installing software or creating accounts |
| PER-02 | Priya Nair | Student / Academic | Edit a PDF form or template in Word without paying for a tool or uploading sensitive work to an untrustworthy site |
| PER-03 | Dana Okafor | Freelancer / Small Business Owner | Turn client-supplied PDF contracts and briefs into editable DOCX files efficiently, within a tight workflow |

---

## PER-01: Marcus Webb

**Role & Context:**
Marcus is an operations coordinator at a mid-size professional services firm. He receives 10–20 PDF documents per week — contracts from vendors, reports from partners, templated forms from internal teams — that he or a colleague needs to edit before passing along. He works entirely in a browser-based environment on a Windows laptop and relies on Microsoft Word as his primary editor. Marcus has no IT admin rights to install new desktop software, and his organization's IT policy blocks most browser extension installs. He's tried Adobe Acrobat online but objects to creating yet another account, and his firm prohibits uploading confidential contracts to untrusted external services with unclear data retention policies.

**Goals:**
- Get a vendor contract or internal report into Word in under two minutes so he can redline it and move on (F0, F1, F2)
- Trust that uploaded documents are not stored or logged by the service after conversion (F4)
- Understand exactly what's happening at each step — no silent failures or blank results (F3)
- Avoid installing desktop software or creating accounts (F0, product scope)

**Pain Points:**
- PDFs from external partners cannot be edited directly in Word without a conversion step (PRD §2)
- Desktop tools like Adobe Acrobat and LibreOffice require installation he can't do at work (PRD §2)
- Most online converters require account creation or have ambiguous privacy practices — a compliance risk for contract documents (PRD §2)
- Free tools frequently mangle heading hierarchy and list formatting, requiring heavy manual cleanup (PRD §2)
- Conversion failures with no explanation leave him guessing what went wrong and whether to retry (PRD §2)

**Technical Expertise:** Intermediate — comfortable with all standard web applications; not a developer; avoids anything requiring installation or configuration.

**Top Tasks:**
1. Upload a received PDF contract or report and download the DOCX (daily/weekly, critical — core conversion journey)
2. Verify the download file is correctly named and corresponds to the original PDF (per conversion, high)
3. Read status messages to confirm conversion succeeded before opening the DOCX in Word (per conversion, high)
4. Retry after a failed conversion without losing his place or refreshing the page (occasional, medium)

**Success Criteria:**
- Completes an upload → convert → download cycle in under 60 seconds end-to-end
- Converted DOCX retains text content, headings, and paragraph structure with no manual cleanup required for straightforward documents
- Never sees a file marked as stored or retained after download confirmation
- Error messages tell him exactly why a conversion failed (too large, wrong format) so he can act on it immediately

---

## PER-02: Priya Nair

**Role & Context:**
Priya is a graduate student in social sciences who frequently works with PDF forms — scholarship applications, ethics board submissions, registration templates — that she needs to fill in or modify before submitting. She uses both a personal MacBook and university lab computers, switching between browsers (Safari, Chrome) depending on where she is. She has no budget for subscription software, finds Adobe Acrobat's paywalled features frustrating, and is cautious about uploading her university coursework or personal information to services that run ads or have opaque data policies. She's a relatively frequent user of web-based productivity tools but reads privacy notices more carefully than most.

**Goals:**
- Quickly convert a PDF form or template into an editable DOCX so she can type into it in Word or Google Docs (F0, F1, F2)
- Feel confident that her uploaded document — which may contain personal or academic work — is deleted immediately after she downloads the converted file (F4)
- Complete the conversion without creating an account or providing an email address (product scope)
- Get clear feedback if a conversion fails — especially if the file is a scanned image — so she can find an alternative (F3)

**Pain Points:**
- PDF forms cannot be filled in natively in Word; she needs a conversion step every time she receives one (PRD §2)
- Free online converters often show ads, request email sign-up, or have terms that allow file retention for analytics (PRD §2)
- When a scanned PDF produces a blank DOCX, tools give no explanation, leaving her to guess whether the tool failed or the PDF was image-only (PRD §2)
- Moving between a MacBook and lab computers means she needs a tool that works in any modern browser with no installation (PRD §2)

**Technical Expertise:** Intermediate — fluent with web apps and Google Workspace; privacy-aware; not a developer.

**Top Tasks:**
1. Upload a PDF form and download the editable DOCX version (occasional — a few times per semester, but critical each time)
2. Confirm the tool's privacy behavior before uploading (pre-upload, high — trust gate)
3. Receive a specific, actionable error message if the PDF is scanned/image-only (occasional, high)
4. Use the tool keyboard-only when on a shared lab computer without a mouse (occasional, medium)

**Success Criteria:**
- Can complete a full conversion cycle on any current-version browser (Safari, Chrome, Firefox, Edge) without installing anything
- No account or email address required at any point in the workflow
- Server confirms (via behavior and UI messaging) that files are deleted after download — she never needs to wonder
- If her PDF is a scanned image, she receives an explicit, plain-language message explaining the limitation rather than a blank DOCX

---

## PER-03: Dana Okafor

**Role & Context:**
Dana runs a small independent consulting practice — two people including herself — and regularly receives PDF documents from clients: statements of work, reference contracts, brief templates, and rate card tables she needs to adapt. She works primarily on a Windows PC using Microsoft Word and charges by the hour, so any friction in her document workflow has a direct cost. She's tried several online converters and has a clear hierarchy: she'll pay for a tool that works reliably, but she won't pay for one that also mishandles formatting. Her biggest gripe is losing table structures and numbered list formatting in converted documents, which can take 20–30 minutes to manually restore. She values speed and output quality above all else.

**Goals:**
- Convert client-supplied PDFs (contracts, briefs, rate tables) into DOCX files that retain tables, numbered lists, and heading structure with minimal cleanup (F1, F2)
- Finish the upload → download cycle fast enough to not break her work rhythm — ideally under 30 seconds (F0, F1, F2, NFR Performance)
- Get an honest, specific error message if a file fails so she can decide whether to try a different tool rather than wait for a silent retry (F3)
- Avoid per-conversion fees or subscription locks for a tool she uses only a few times per week (product scope)

**Pain Points:**
- Free converters routinely corrupt table layouts and numbered lists, requiring manual reconstruction that kills her hourly efficiency (PRD §2)
- Tools that silently return a poorly-formatted DOCX without flagging conversion quality leave her no choice but to open and audit every result (PRD §2)
- Large client PDFs (40–50 page SoWs) sometimes hit file size limits or time out with no warning (PRD §2, F4)
- She has no time to troubleshoot opaque errors — she needs a converter that either works or tells her clearly why it didn't (PRD §2)

**Technical Expertise:** Intermediate-high — comfortable with SaaS tools, understands file formats and browser behavior, not a developer; values reliability and output quality over features.

**Top Tasks:**
1. Upload a client PDF contract or SoW and download the DOCX ready for Word editing (several times per week, critical)
2. Quickly assess output quality — scan headings, tables, and lists in the DOCX — before committing edits (per conversion, high)
3. Understand file size limits before uploading a large document (per large upload, medium)
4. Retry with a different file if conversion fails, without navigating away or losing context (occasional, medium)

**Success Criteria:**
- Median conversion time ≤15 seconds for typical client PDFs (under 10 pages)
- Converted DOCX preserves table structures and numbered lists accurately enough to require zero manual layout reconstruction for straightforward documents
- File size limit is communicated clearly at upload — not discovered after a failed attempt
- Error messages identify the specific failure mode (too large, unsupported, timeout) and suggest next steps

---

## Persona Relationships

| Interaction | Who | Nature |
|---|---|---|
| PER-01 ↔ Product | Marcus uses the tool as a solo utility within his corporate workflow; no interaction with other personas | Individual, professional, recurring |
| PER-02 ↔ Product | Priya uses the tool infrequently but evaluates it carefully at the trust/privacy layer before uploading | Individual, privacy-gated, occasional |
| PER-03 ↔ Product | Dana uses the tool as a productivity tool embedded in her client-delivery workflow; quality of output directly impacts her work output | Individual, quality-critical, semi-frequent |
| PER-01 ↔ PER-03 | Both deal with professional/contract documents and share a pain point around formatting loss and silent failures; PER-03 is more quality-sensitive and time-pressured | Overlapping needs, different priority weights |
| PER-01 ↔ PER-02 | Both are privacy-conscious and dislike account-gated tools; PER-02 has stronger privacy concerns and explicit accessibility needs | Overlapping values, different context |

All three personas operate independently — there is no multi-user or collaborative workflow in PDFConverter v1.

---

## Feature-Persona Matrix

| Feature ID | Feature Name | PER-01 Marcus | PER-02 Priya | PER-03 Dana |
|---|---|---|---|---|
| F0 | File Upload Interface | **Primary** | **Primary** | **Primary** |
| F1 | Server-Side PDF-to-DOCX Conversion | **Primary** | **Primary** | **Primary** |
| F2 | DOCX File Download | **Primary** | **Primary** | **Primary** |
| F3 | User Feedback & Status Communication | **Primary** | **Primary** | **Primary** |
| F4 | File Security & Privacy Controls | **Secondary** (policy compliance) | **Primary** (personal data concern) | **Secondary** (professional trust) |

**Legend:** Primary = core to this persona's goal; Secondary = important but not the primary driver for this persona; None = not relevant.

**Notes:**
- All features are P0 in the PRD and all personas rely on F0–F3 as the end-to-end conversion journey.
- F4 (Security & Privacy) is Primary for PER-02 because privacy assurance is her trust gate before she uploads at all. For PER-01 and PER-03 it is Secondary — important for compliance and professional trust, but not a blocker that overrides the conversion task.

---

*Document generated: 2026-05-11 | Project: PDFConverter | Version: 1.0*
*Derived from PRD-PDFConverter.md v1.0 — Sections 2, 5, 7*
