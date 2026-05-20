import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'mobile-320',
      use: { ...devices['iPhone SE'], viewport: { width: 320, height: 568 } },
    },
    {
      name: 'mobile-375',
      use: { ...devices['iPhone 12'], viewport: { width: 375, height: 667 } },
    },
    {
      name: 'mobile-414',
      use: { ...devices['iPhone 14 Pro Max'], viewport: { width: 414, height: 896 } },
    },
    {
      name: 'webkit-320',
      use: {
        ...devices['iPhone SE'],
        browserName: 'webkit',
        viewport: { width: 320, height: 568 },
      },
    },
    {
      name: 'webkit-375',
      use: {
        ...devices['iPhone 12'],
        browserName: 'webkit',
        viewport: { width: 375, height: 667 },
      },
    },
    {
      name: 'webkit-414',
      use: {
        ...devices['iPhone 14 Pro Max'],
        browserName: 'webkit',
        viewport: { width: 414, height: 896 },
      },
    },
  ],
});
