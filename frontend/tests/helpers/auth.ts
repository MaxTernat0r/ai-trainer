import type { Page } from '@playwright/test';

export const TEST_EMAIL = 'mobile-test@example.com';
export const TEST_PASSWORD = 'mobile-test-pass-123';

export async function loginAsTestUser(page: Page): Promise<void> {
  await page.goto('/login');
  await page.fill('input[type=email], input[name=email]', TEST_EMAIL);
  await page.fill('input[type=password], input[name=password]', TEST_PASSWORD);
  await page.click('button[type=submit]');
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
}

export async function expectNoHorizontalScroll(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (overflow.scrollWidth > overflow.clientWidth) {
    throw new Error(
      `Horizontal scroll detected: scrollWidth=${overflow.scrollWidth} clientWidth=${overflow.clientWidth}`
    );
  }
}
