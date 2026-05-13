'use strict';

// ─── Constants ────────────────────────────────────────────────────────────────
const MAX_FILE_SIZE_BYTES = 52428800; // 50 MB — from TechArch

// ─── DOM References ───────────────────────────────────────────────────────────
const dropZone       = document.getElementById('drop-zone');
const fileInput      = document.getElementById('file-input');
const browseBtn      = document.getElementById('browse-btn');
const fileInfo       = document.getElementById('file-info');
const fileName       = document.getElementById('file-name');
const fileSize       = document.getElementById('file-size');
const convertBtn     = document.getElementById('convert-btn');
const uploadProgress = document.getElementById('upload-progress');
const statusBanner   = document.getElementById('status-banner');
const errorDetail    = document.getElementById('error-detail');
const tryAgainBtn    = document.getElementById('try-again-btn');
const convertAnotherLink = document.getElementById('convert-another-link');
const downloadBtn        = document.getElementById('download-btn');

// ─── State ────────────────────────────────────────────────────────────────────
let currentState = 'IDLE';
let selectedFile  = null;
let lastJobId     = null;   // Stored for download-btn re-trigger
let lastFilename  = null;

// ─── Error Message Map — primary messages (FRD §F03, exact strings) ──────────
const ERROR_MESSAGES = {
  INVALID_FILE_TYPE:  "This file doesn't appear to be a valid PDF.",
  FILE_TOO_LARGE:     'Your file is too large to convert.',
  CONVERSION_TIMEOUT: 'Conversion took too long and was cancelled.',
  CONVERSION_FAILED:  "We couldn't convert this PDF.",
  IMAGE_ONLY_PDF:     'This PDF contains only images and cannot be converted.',
  SERVER_BUSY:        'The server is busy. Please try again in a moment.',
  INTERNAL_ERROR:     'Something went wrong on our end.',
  JOB_NOT_FOUND:      'Your conversion result has expired.',
  JOB_FAILED:         'Conversion job failed. Please try again.',
  INVALID_JOB_ID:     'Invalid job reference. Please try again.',
};

// ─── Error Detail Map — secondary explanatory text (FRD §F03) ────────────────
const ERROR_DETAILS = {
  INVALID_FILE_TYPE:  'The server was unable to verify the file as a PDF document.',
  FILE_TOO_LARGE:     'Maximum file size is 50 MB. Please try a smaller PDF.',
  CONVERSION_TIMEOUT: 'Large or complex PDFs may exceed the processing time limit. Try a smaller document.',
  CONVERSION_FAILED:  'The document may use an unsupported format or structure. Try re-saving it from the source application.',
  IMAGE_ONLY_PDF:     'Scanned or image-based PDFs require OCR, which is not supported in this version.',
  SERVER_BUSY:        'Too many files are being converted simultaneously.',
  INTERNAL_ERROR:     'An unexpected server error occurred. Please try again.',
  JOB_NOT_FOUND:      'The download link is no longer valid. Please convert the file again.',
  JOB_FAILED:         '',
  INVALID_JOB_ID:     '',
};

// ─── State Machine ────────────────────────────────────────────────────────────
function setState(newState, message) {
  currentState = newState;

  // Remove all state modifier classes from status banner
  statusBanner.className = 'status-banner';
  statusBanner.textContent = message || '';

  // Reset all elements to base visibility
  uploadProgress.hidden = true;
  errorDetail.hidden    = true;
  tryAgainBtn.hidden    = true;
  convertAnotherLink.hidden = true;
  if (downloadBtn) downloadBtn.hidden = true;

  switch (newState) {
    case 'IDLE':
      convertBtn.disabled = (selectedFile === null);
      dropZone.removeAttribute('aria-disabled');
      break;

    case 'UPLOADING':
      statusBanner.classList.add('status-banner--uploading');
      statusBanner.textContent = message || 'Uploading\u2026';
      uploadProgress.value  = 0;
      uploadProgress.hidden = false;
      convertBtn.disabled   = true;
      dropZone.setAttribute('aria-disabled', 'true');
      break;

    case 'CONVERTING':
      statusBanner.classList.add('status-banner--converting');
      statusBanner.textContent = message || 'Converting your document\u2026';
      uploadProgress.hidden = false;
      uploadProgress.value  = 100; // Upload complete; show full bar during conversion
      convertBtn.disabled   = true;
      break;

    case 'SUCCESS':
      statusBanner.classList.add('status-banner--success');
      statusBanner.textContent = message || '\u2713 Your DOCX is ready!';
      convertAnotherLink.hidden = false;
      if (downloadBtn) downloadBtn.hidden = false;
      convertBtn.disabled = true;
      break;

    case 'ERROR':
      statusBanner.classList.add('status-banner--error');
      statusBanner.textContent = message || 'An error occurred.';
      errorDetail.hidden = true;
      tryAgainBtn.hidden  = false;
      convertBtn.disabled = true;
      break;
  }
}

// ─── File Validation ──────────────────────────────────────────────────────────
function validateFile(file) {
  // Type validation: check BOTH file.type AND extension (US-0.3)
  const isPdfType = file.type === 'application/pdf';
  const isPdfExt  = file.name.toLowerCase().endsWith('.pdf');

  if (!isPdfType && !isPdfExt) {
    showInlineError('Please select a PDF file.');
    return false;
  }

  // Size validation: MAX_FILE_SIZE_BYTES = 52,428,800 (50 MB) (US-0.4)
  if (file.size > MAX_FILE_SIZE_BYTES) {
    showInlineError('File too large. Maximum size is 50 MB.');
    return false;
  }

  return true;
}

function showInlineError(message) {
  selectedFile = null;
  fileInfo.hidden = true;
  convertBtn.disabled = true;
  errorDetail.textContent = message;
  errorDetail.hidden = false;
  statusBanner.className = 'status-banner';
  // Announce to screen readers via aria-live region
  statusBanner.textContent = message;
}

// ─── File Selection ───────────────────────────────────────────────────────────
function handleFileSelected(file) {
  // Clear previous error state
  errorDetail.hidden = true;
  statusBanner.className = 'status-banner';
  statusBanner.textContent = '';

  if (!validateFile(file)) return;

  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  fileInfo.hidden = false;
  convertBtn.disabled = false;
}

function formatBytes(bytes) {
  if (bytes < 1024)        return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ─── Drag-and-Drop Handlers (US-0.2) ─────────────────────────────────────────
dropZone.addEventListener('dragenter', (e) => {
  e.preventDefault();
  if (currentState !== 'IDLE') return;
  dropZone.classList.add('drop-zone--dragover');
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault(); // Prevent browser default (open file)
  if (currentState !== 'IDLE') return;
  dropZone.classList.add('drop-zone--dragover');
  e.dataTransfer.dropEffect = 'copy';
});

dropZone.addEventListener('dragleave', (e) => {
  // Only remove class when leaving the drop zone entirely (not a child element)
  if (!dropZone.contains(e.relatedTarget)) {
    dropZone.classList.remove('drop-zone--dragover');
  }
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drop-zone--dragover');
  if (currentState !== 'IDLE') return;

  const file = e.dataTransfer.files[0];
  if (file) handleFileSelected(file);
});

// ─── File Picker Handlers (US-0.1) ────────────────────────────────────────────
browseBtn.addEventListener('click', (e) => {
  e.stopPropagation(); // Prevent drop zone click handler from firing too
  fileInput.click();
});

dropZone.addEventListener('click', (e) => {
  // Clicking anywhere on the drop zone (except the browse button) opens picker
  if (e.target !== browseBtn && currentState === 'IDLE') {
    fileInput.click();
  }
});

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) handleFileSelected(file);
});

// ─── Keyboard Accessibility (US-0.6) ─────────────────────────────────────────
dropZone.addEventListener('keydown', (e) => {
  if ((e.key === 'Enter' || e.key === ' ') && currentState === 'IDLE') {
    e.preventDefault();
    fileInput.click();
  }
});

// ─── Convert Button → XHR Upload (US-0.5) ────────────────────────────────────
// IMPORTANT: Use XMLHttpRequest — NOT fetch. XHR is required for upload.onprogress events.
convertBtn.addEventListener('click', () => {
  if (!selectedFile || currentState !== 'IDLE') return;

  setState('UPLOADING');

  const formData = new FormData();
  formData.append('file', selectedFile);

  const xhr = new XMLHttpRequest();

  // Track upload progress (0→100%) — ONLY possible with XHR, not fetch
  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      uploadProgress.value = Math.round((e.loaded / e.total) * 100);
    }
  };

  xhr.upload.onload = () => {
    // Upload complete; transition to CONVERTING state while server processes
    setState('CONVERTING');
  };

  xhr.onload = () => {
    if (xhr.status === 200) {
      let data;
      try {
        data = JSON.parse(xhr.responseText);
      } catch {
        setState('ERROR', ERROR_MESSAGES.INTERNAL_ERROR);
        if (ERROR_DETAILS.INTERNAL_ERROR) {
          errorDetail.textContent = ERROR_DETAILS.INTERNAL_ERROR;
          errorDetail.hidden = false;
        }
        return;
      }
      lastJobId    = data.job_id;
      lastFilename = data.filename;
      // Trigger download: GET /api/download/{job_id}
      triggerDownload(lastJobId, lastFilename);
      setState('SUCCESS');
    } else {
      let errorCode = 'INTERNAL_ERROR';
      try {
        const errData = JSON.parse(xhr.responseText);
        errorCode = errData.error_code || 'INTERNAL_ERROR';
      } catch { /* ignore parse error */ }
      const primaryMsg = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES.INTERNAL_ERROR;
      const detailMsg  = ERROR_DETAILS[errorCode]  || '';
      setState('ERROR', primaryMsg);
      if (detailMsg) {
        errorDetail.textContent = detailMsg;
        errorDetail.hidden = false;
      }
    }
  };

  xhr.onerror = () => {
    setState('ERROR', 'Upload failed. Please check your connection and try again.');
  };

  xhr.ontimeout = () => {
    setState('ERROR', ERROR_MESSAGES.CONVERSION_TIMEOUT);
    if (ERROR_DETAILS.CONVERSION_TIMEOUT) {
      errorDetail.textContent = ERROR_DETAILS.CONVERSION_TIMEOUT;
      errorDetail.hidden = false;
    }
  };

  xhr.open('POST', '/api/convert');
  xhr.send(formData);
});

// ─── Download Trigger ─────────────────────────────────────────────────────────
function triggerDownload(jobId, filename) {
  // Use an invisible anchor with the download attribute
  const a = document.createElement('a');
  a.href = '/api/download/' + jobId;
  a.download = filename || 'converted.docx';
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// ─── Download DOCX Button Handler (SUCCESS state re-download) ─────────────────
// The download-btn is shown in SUCCESS state. Clicking it re-triggers the download
// via the stored lastJobId. If the file was already deleted (Phase 4 one-time
// download policy), the server returns 404 and we transition SUCCESS→ERROR.
if (downloadBtn) {
  downloadBtn.addEventListener('click', () => {
    if (!lastJobId) return;
    fetch('/api/download/' + lastJobId, { method: 'GET', redirect: 'manual' })
      .then((response) => {
        if (response.ok) {
          // File still available — trigger download via anchor
          triggerDownload(lastJobId, lastFilename);
        } else if (response.status === 404 || response.status === 0) {
          // File was already deleted after first download (status 0 = opaque redirect)
          setState('ERROR', ERROR_MESSAGES.JOB_NOT_FOUND);
          if (ERROR_DETAILS.JOB_NOT_FOUND) {
            errorDetail.textContent = ERROR_DETAILS.JOB_NOT_FOUND;
            errorDetail.hidden = false;
          }
        } else {
          setState('ERROR', ERROR_MESSAGES.INTERNAL_ERROR);
        }
      })
      .catch(() => {
        setState('ERROR', 'Upload failed. Please check your connection and try again.');
      });
  });
}

// ─── Try Again Handler ────────────────────────────────────────────────────────
tryAgainBtn.addEventListener('click', () => {
  // Reset to IDLE: clear file selection, reset form, hide all status elements
  selectedFile = null;
  fileInput.value = '';    // Clear the file input
  fileInfo.hidden = true;
  fileName.textContent = '';
  fileSize.textContent = '';
  uploadProgress.value  = 0;
  setState('IDLE');
});

// ─── Convert Another File Handler ─────────────────────────────────────────────
convertAnotherLink.addEventListener('click', (e) => {
  e.preventDefault();
  selectedFile = null;
  fileInput.value = '';
  fileInfo.hidden = true;
  fileName.textContent = '';
  fileSize.textContent = '';
  uploadProgress.value  = 0;
  setState('IDLE');
});

// ─── Initial State ────────────────────────────────────────────────────────────
setState('IDLE');
