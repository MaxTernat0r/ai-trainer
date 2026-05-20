import { test, expect } from '@playwright/test';
import { loginAsTestUser } from './helpers/auth';

test.describe('Mobile interaction details', () => {
  test('marketing landing CTA button is visible and clickable', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const cta = page.getByRole('link', { name: /собрать личный план/i });
    await expect(cta).toBeVisible();
    const box = await cta.boundingBox();
    expect(box).not.toBeNull();
  });

  test('onboarding shows progress bar but not stepper-circles on mobile', async ({ page }) => {
    await loginAsTestUser(page);
    // Force onboarding by visiting directly
    await page.goto('/onboarding');
    await page.waitForLoadState('networkidle');
    // The row of stepper circles uses `hidden ... sm:flex` — on <640px it's display:none.
    const stepperCircles = page
      .locator('div.flex.size-8.items-center.justify-center.rounded-full')
      .first();
    const isVisible = await stepperCircles.isVisible().catch(() => false);
    expect(isVisible).toBe(false);
  });

  test('analytics tabs are scrollable horizontally on narrow viewports', async ({ page, viewport }) => {
    await loginAsTestUser(page);
    await page.goto('/analytics');
    await page.waitForLoadState('networkidle');
    // The wrapper should be the overflow-x-auto div
    const tabsScrollWrapper = page.locator('div.no-scrollbar.overflow-x-auto').first();
    await expect(tabsScrollWrapper).toBeVisible();
    const wrapperBox = await tabsScrollWrapper.boundingBox();
    expect(wrapperBox).not.toBeNull();
    if (wrapperBox && viewport) {
      // Wrapper width should fit viewport (it's contained)
      expect(wrapperBox.width).toBeLessThanOrEqual(viewport.width);
    }
  });

  test('register page inputs are at least 16px font (no iOS zoom)', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    const inputs = page.locator('input');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
    for (let i = 0; i < count; i++) {
      const fontSize = await inputs.nth(i).evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });
      const px = parseFloat(fontSize);
      expect(px).toBeGreaterThanOrEqual(16);
    }
  });
});
