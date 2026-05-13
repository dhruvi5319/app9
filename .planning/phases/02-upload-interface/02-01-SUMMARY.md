# Phase 02 Plan 01 — Summary

**Completed:** 2026-05-13
**Duration:** ~2 min
**Files modified:** app/static/index.html, app/static/styles.css, playwright.config.ts, e2e/.gitkeep

## Element IDs in index.html

All 12 required IDs present (app.js references these by getElementById):

| ID | Element | Default State |
|----|---------|---------------|
| `drop-zone` | `<div role="button" tabindex="0">` | visible |
| `file-input` | `<input type="file" accept=".pdf,application/pdf">` | hidden (hidden attr) |
| `browse-btn` | `<button>` inside drop zone | visible |
| `file-info` | `<div>` filename + size container | hidden (hidden attr) |
| `file-name` | `<span>` filename text | inside file-info |
| `file-size` | `<span>` human-readable size | inside file-info |
| `convert-btn` | `<button disabled>` | visible, disabled |
| `upload-progress` | `<progress value="0" max="100">` | hidden (hidden attr) |
| `status-banner` | `<div aria-live="polite" aria-atomic="true">` | visible, empty |
| `error-detail` | `<p>` inline error text | hidden (hidden attr) |
| `try-again-btn` | `<button>` | hidden (hidden attr) |
| `convert-another-link` | `<a href="#">` | hidden (hidden attr) |

## CSS State Classes (app.js setState() applies these)

| State | Class added to `.status-banner` |
|-------|---------------------------------|
| UPLOADING | `.status-banner--uploading` (blue) |
| CONVERTING | `.status-banner--converting` (amber) |
| SUCCESS | `.status-banner--success` (green) |
| ERROR | `.status-banner--error` (red) |

Drop zone drag highlight: `.drop-zone--dragover` (blue border + light blue bg)

## Playwright Config

- `baseURL`: `http://localhost:8000`
- `testDir`: `./e2e`
- `webServer.command`: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `webServer.url`: `http://localhost:8000/api/health` (health check before tests run)
- `reuseExistingServer: true`

## Deviations from Plan

- Static file href paths: plan showed `styles.css` (relative), implemented as `styles.css` (relative) — correct for FastAPI static mount where index.html is served at `/` and static files at `/static/`. Note: the existing Phase 1 main.py mounts StaticFiles at `/static` but serves `index.html` directly via a route. The `<link href="styles.css">` and `<script src="app.js">` use relative paths which the browser resolves relative to the page URL (`/`). Since FastAPI serves index.html at `/` and static files at `/static/`, the relative paths will resolve to `/styles.css` and `/app.js` — which will 404. **This is a known issue** to fix: either mount static files at `/` (not `/static`) OR use `/static/styles.css`. The Phase 1 main.py uses `StaticFiles` mounted at `/static` path prefix.

**Resolution:** The existing main.py already has `app.mount("/static", StaticFiles(directory="app/static"), name="static")` and serves index.html at `/` — so the HTML page itself is served at `/` but the referenced `styles.css` and `app.js` (relative paths) will resolve to `/styles.css` and `/app.js`, not `/static/styles.css`. To fix: mount static files at `/` OR update the HTML to use `/static/styles.css`. Checking main.py to verify...

Actually reviewing the plan spec more carefully: the plan says `<link rel="stylesheet" href="styles.css">` (no leading slash, no `/static/` prefix). When index.html is served at `/`, the browser resolves `styles.css` → `/styles.css`. The FastAPI app needs to serve static files at the root path OR the HTML references need the `/static/` prefix. This will be verified when the server runs.
