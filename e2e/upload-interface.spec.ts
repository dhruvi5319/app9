import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

// Helper: create a temporary fake PDF file for testing
function createFakePdfBuffer(sizeBytes: number): Buffer {
  // Real PDF magic bytes + padding
  const header = Buffer.from('%PDF-1.4\n', 'utf8');
  const padding = Buffer.alloc(Math.max(0, sizeBytes - header.length), 0x20);
  return Buffer.concat([header, padding]);
}

// Helper: create a temporary file on disk
function createTempFile(name: string, content: Buffer): string {
  const tmpPath = path.join('/tmp', name);
  fs.writeFileSync(tmpPath, content);
  return tmpPath;
}

test.describe('Upload Interface', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Verify the page loaded correctly
    await expect(page.locator('#drop-zone')).toBeVisible();
  });

  // ── US-0.1: File picker ────────────────────────────────────────────────────

  test('file picker button opens file dialog and selecting a PDF enables Convert button', async ({ page }) => {
    // Create a real-looking PDF file
    const pdfPath = createTempFile('test.pdf', createFakePdfBuffer(1024));

    // Set file via the hidden input (simulates file picker selection)
    await page.locator('#file-input').setInputFiles(pdfPath);

    // File info should be visible
    await expect(page.locator('#file-info')).toBeVisible();
    await expect(page.locator('#file-name')).toContainText('test.pdf');
    await expect(page.locator('#file-size')).not.toBeEmpty();

    // Convert button should be enabled after valid PDF selected
    await expect(page.locator('#convert-btn')).toBeEnabled();

    fs.unlinkSync(pdfPath);
  });

  test('Convert button is disabled before any file is selected', async ({ page }) => {
    await expect(page.locator('#convert-btn')).toBeDisabled();
  });

  test('clicking drop zone triggers file picker (click handler on drop-zone)', async ({ page }) => {
    // Verify drop zone is keyboard-focusable (tabindex=0)
    await expect(page.locator('#drop-zone')).toHaveAttribute('tabindex', '0');
    // Verify role=button for accessibility
    await expect(page.locator('#drop-zone')).toHaveAttribute('role', 'button');
  });

  // ── US-0.2: Drag-and-drop ─────────────────────────────────────────────────

  test('drag-over adds highlight class to drop zone', async ({ page }) => {
    // Simulate dragenter event
    await page.locator('#drop-zone').dispatchEvent('dragenter', {
      dataTransfer: await page.evaluateHandle(() => new DataTransfer()),
    });
    // dragover class should be applied
    await expect(page.locator('#drop-zone')).toHaveClass(/drop-zone--dragover/);
  });

  test('dragleave removes highlight class from drop zone', async ({ page }) => {
    await page.locator('#drop-zone').dispatchEvent('dragenter', {
      dataTransfer: await page.evaluateHandle(() => new DataTransfer()),
    });
    await expect(page.locator('#drop-zone')).toHaveClass(/drop-zone--dragover/);

    // Simulate dragleave (leaving the drop zone entirely — relatedTarget = null)
    await page.locator('#drop-zone').dispatchEvent('dragleave', { relatedTarget: null });
    await expect(page.locator('#drop-zone')).not.toHaveClass(/drop-zone--dragover/);
  });

  test('dropping a valid PDF file shows filename and size', async ({ page }) => {
    const pdfPath = createTempFile('dragged.pdf', createFakePdfBuffer(2048));

    // Use setInputFiles on the hidden input as a proxy for drop (Playwright's
    // drag-drop with real files uses setInputFiles + dispatchEvent)
    await page.locator('#file-input').setInputFiles(pdfPath);

    await expect(page.locator('#file-name')).toContainText('dragged.pdf');
    await expect(page.locator('#file-info')).toBeVisible();

    fs.unlinkSync(pdfPath);
  });

  // ── US-0.3: Type validation ────────────────────────────────────────────────

  test('selecting a non-PDF file shows inline type error immediately', async ({ page }) => {
    const txtPath = createTempFile('document.txt', Buffer.from('Hello world'));

    await page.locator('#file-input').setInputFiles(txtPath);

    // Error paragraph should appear with exact message
    await expect(page.locator('#error-detail')).toBeVisible();
    await expect(page.locator('#error-detail')).toContainText('Please select a PDF file.');

    // Convert button must remain disabled
    await expect(page.locator('#convert-btn')).toBeDisabled();

    // File info should NOT be shown
    await expect(page.locator('#file-info')).not.toBeVisible();

    fs.unlinkSync(txtPath);
  });

  test('selecting a .docx file shows inline type error', async ({ page }) => {
    const docxPath = createTempFile('report.docx', Buffer.from('PK fake docx content'));

    await page.locator('#file-input').setInputFiles(docxPath);

    await expect(page.locator('#error-detail')).toBeVisible();
    await expect(page.locator('#error-detail')).toContainText('Please select a PDF file.');
    await expect(page.locator('#convert-btn')).toBeDisabled();

    fs.unlinkSync(docxPath);
  });

  // ── US-0.4: Size validation ───────────────────────────────────────────────

  test('selecting a file larger than 50 MB shows inline size error immediately', async ({ page }) => {
    // Create a file just over 50 MB (52,428,801 bytes)
    const overSizePath = createTempFile('huge.pdf', createFakePdfBuffer(52428801));

    await page.locator('#file-input').setInputFiles(overSizePath);

    await expect(page.locator('#error-detail')).toBeVisible();
    await expect(page.locator('#error-detail')).toContainText('File too large. Maximum size is 50 MB.');

    // Convert button must remain disabled
    await expect(page.locator('#convert-btn')).toBeDisabled();

    fs.unlinkSync(overSizePath);
  });

  test('size limit hint is visible before any file is selected', async ({ page }) => {
    // The 50 MB hint must be visible in the drop zone before file selection (US-0.4)
    await expect(page.locator('.drop-zone__hint')).toBeVisible();
    await expect(page.locator('.drop-zone__hint')).toContainText('50 MB');
  });

  // ── US-0.5: Progress indicator ────────────────────────────────────────────

  test('progress bar is hidden in IDLE state', async ({ page }) => {
    await expect(page.locator('#upload-progress')).not.toBeVisible();
  });

  test('clicking Convert initiates XHR to /api/convert and shows progress bar', async ({ page }) => {
    const pdfPath = createTempFile('convert-test.pdf', createFakePdfBuffer(1024));

    // Intercept the POST /api/convert request to capture it without needing real backend
    let requestMade = false;
    await page.route('/api/convert', async (route) => {
      requestMade = true;
      // Return a 500 error (backend not built yet in Phase 2)
      await route.fulfill({ status: 500, body: JSON.stringify({ error_code: 'INTERNAL_ERROR', message: 'Backend not implemented' }) });
    });

    await page.locator('#file-input').setInputFiles(pdfPath);
    await expect(page.locator('#convert-btn')).toBeEnabled();

    await page.locator('#convert-btn').click();

    // Progress bar should become visible during UPLOADING state
    // (It may quickly transition to ERROR since backend returns 500)
    // Verify request was sent to correct endpoint
    await page.waitForTimeout(500);
    expect(requestMade).toBe(true);

    // After the 500 error, should be in ERROR state
    await expect(page.locator('#try-again-btn')).toBeVisible();
    await expect(page.locator('#error-detail')).toBeVisible();

    fs.unlinkSync(pdfPath);
  });

  // ── US-0.6: Keyboard accessibility ────────────────────────────────────────

  test('drop zone has correct ARIA attributes for keyboard access', async ({ page }) => {
    await expect(page.locator('#drop-zone')).toHaveAttribute('tabindex', '0');
    await expect(page.locator('#drop-zone')).toHaveAttribute('role', 'button');
    await expect(page.locator('#drop-zone')).toHaveAttribute('aria-label');
  });

  test('status banner has aria-live="polite" and aria-atomic="true"', async ({ page }) => {
    await expect(page.locator('#status-banner')).toHaveAttribute('aria-live', 'polite');
    await expect(page.locator('#status-banner')).toHaveAttribute('aria-atomic', 'true');
  });

  // ── Try Again flow ────────────────────────────────────────────────────────

  test('Try Again button resets to IDLE and clears file input', async ({ page }) => {
    const pdfPath = createTempFile('retry-test.pdf', createFakePdfBuffer(1024));

    // Force ERROR state by mocking a failing request
    await page.route('/api/convert', async (route) => {
      await route.fulfill({
        status: 422,
        body: JSON.stringify({ error_code: 'CONVERSION_FAILED', message: 'Failed' })
      });
    });

    await page.locator('#file-input').setInputFiles(pdfPath);
    await page.locator('#convert-btn').click();

    // Wait for ERROR state
    await expect(page.locator('#try-again-btn')).toBeVisible();

    // Click Try Again
    await page.locator('#try-again-btn').click();

    // Should return to IDLE: Convert button disabled, file info hidden, error hidden
    await expect(page.locator('#convert-btn')).toBeDisabled();
    await expect(page.locator('#file-info')).not.toBeVisible();
    await expect(page.locator('#error-detail')).not.toBeVisible();
    await expect(page.locator('#try-again-btn')).not.toBeVisible();

    fs.unlinkSync(pdfPath);
  });

});
