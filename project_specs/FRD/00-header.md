# Functional Requirements Document
# PDF to DOCX Converter (PDFConverter)

**Version:** 1.0
**Date:** 2026-05-11
**Status:** Draft
**Based on:** PRD-PDFConverter.md v1.0

---

## Scope

This document defines the complete functional specification for the PDFConverter web application — a minimal, no-account browser-based tool that converts PDF files to editable DOCX (Microsoft Word) format. It covers all five MVP features (F0–F4), the REST API surface, temporary file storage schema, cross-feature error catalog, and external integration points.

This FRD is authoritative. Downstream implementation agents must treat it as the single source of truth for feature behaviour, validation rules, input/output contracts, and error handling.

---

## How to Read This Document

- **Feature IDs** follow `F{nn}` notation (zero-padded). Each feature chunk is self-contained.
- **API endpoints** are summarised inline per feature and fully specified in `Y1-api.md`.
- **Storage schema** is summarised inline per feature and fully specified in `Y0-schema.md`.
- **Error codes** are referenced inline and catalogued in `Y2-errors.md`.
- **External integrations** are described in `Y3-integrations.md`.
- All HTTP status codes follow RFC 9110.
- All file size references use binary megabytes (1 MB = 1,048,576 bytes) unless otherwise stated.

---

## Table of Contents

| Section | Description |
|---------|-------------|
| [F00 – File Upload Interface](#f00-file-upload-interface) | Browser upload UI, drag-and-drop, client-side validation |
| [F01 – Server-Side PDF-to-DOCX Conversion](#f01-server-side-pdf-to-docx-conversion) | Core conversion engine, temp storage, timeout |
| [F02 – DOCX File Download](#f02-docx-file-download) | Download delivery, filename mapping, cleanup |
| [F03 – User Feedback & Status Communication](#f03-user-feedback--status-communication) | Progress indicators, status messages, retry flow |
| [F04 – File Security & Privacy Controls](#f04-file-security--privacy-controls) | Input validation, no-persistence policy, TTL cleanup |
| [Y0 – Storage Schema](#y0-storage-schema) | Temp directory layout and job metadata |
| [Y1 – API Endpoints](#y1-api-endpoints) | Full REST API specification |
| [Y2 – Error Catalog](#y2-error-catalog) | Cross-feature error codes and HTTP statuses |
| [Y3 – Integrations](#y3-integrations) | External library and system dependencies |

---

## Cross-Cutting Terminology

| Term | Definition |
|------|-----------|
| **PDF** | Portable Document Format file (`.pdf`). The source file uploaded by the user. |
| **DOCX** | Microsoft Word Open XML document format (`.docx`). The output file returned to the user. |
| **Conversion Job** | The server-side lifecycle of a single PDF upload: receive → validate → convert → deliver → clean up. |
| **Temp Directory** | An isolated, server-managed directory (e.g., `/tmp/pdfconverter/`) where uploaded PDFs and generated DOCX files are stored transiently during a conversion job. |
| **Job ID** | A server-generated UUID (v4) uniquely identifying a single conversion job and its associated temp files. |
| **TTL** | Time-To-Live. The maximum duration a temp file may exist on the server before being swept by the cleanup job (default: 60 minutes). |
| **MIME Type** | Media type string (e.g., `application/pdf`) used for server-side file type validation. |
| **Client-Side Validation** | Validation performed in the browser before the upload request is sent. Acts as a UX guard, not a security boundary. |
| **Server-Side Validation** | Authoritative validation performed on the server after receiving the upload. The security boundary. |
| **Orphaned File** | A temp file whose parent conversion job was abandoned (e.g., client disconnected mid-upload) and which was never explicitly cleaned up by the normal workflow. Handled by the TTL sweep. |
| **Image-only PDF** | A PDF whose pages consist entirely of rasterised images with no extractable text layer. Cannot be converted by `pdf2docx` without OCR (out of scope for v1). |

---

## Conventions

- **Required fields** are marked `(required)`.
- **Optional fields** are marked `(optional)`.
- Validation rules use the word **MUST** (mandatory), **SHOULD** (strongly recommended), and **MAY** (permitted but not required).
- Error code format: `UPPER_SNAKE_CASE` string returned in JSON error body.
- All timestamps are ISO 8601 UTC.

---
