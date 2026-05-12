import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 10000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:8000',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Auto-start uvicorn before tests; reuse if already running
  webServer: {
    command: 'uvicorn app.main:app --host 0.0.0.0 --port 8000',
    url: 'http://localhost:8000/api/health',
    reuseExistingServer: true,
    timeout: 15000,
  },
});
