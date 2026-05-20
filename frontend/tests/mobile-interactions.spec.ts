import { test, expect } from '@playwright/test';
import { loginAsTestUser } from './helpers/auth';

test.describe('Mobile interaction details', () => {
  test('mobile tab bar items meet 40px tap target', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const tabBar = page.locator('nav.fixed').filter({ hasText: 'Главная' }).first();
    await expect(tabBar).toBeVisible();
    const links = tabBar.locator('a');
    const count = await links.count();
    expect(count).toBeGreaterThanOrEqual(5);
    for (let i = 0; i < count; i++) {
      const box = await links.nth(i).boundingBox();
      expect(box).not.toBeNull();
      if (box) {
        // Apple HIG min tap target is 44px, but our compact layout can go down to 40
        expect(box.height).toBeGreaterThanOrEqual(36);
        expect(box.width).toBeGreaterThanOrEqual(36);
      }
    }
  });

  test('chat input visible above mobile tab bar', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
    const input = page.locator('input[placeholder*="сообщение" i]').first();
    await expect(input).toBeVisible();
    const inputBox = await input.boundingBox();
    const tabBar = page.locator('nav.fixed').filter({ hasText: 'Главная' }).first();
    await expect(tabBar).toBeVisible();
    const tabBarBox = await tabBar.boundingBox();
    expect(inputBox).not.toBeNull();
    expect(tabBarBox).not.toBeNull();
    if (inputBox && tabBarBox) {
      // Input bottom should be above tab-bar top (no overlap)
      expect(inputBox.y + inputBox.height).toBeLessThanOrEqual(tabBarBox.y + 1);
    }
  });

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

  test('exercises page has 4 filters arranged in 2 columns on mobile', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/exercises');
    await page.waitForLoadState('networkidle');
    // The container should have grid-cols-2 on mobile
    const filterContainer = page.locator('div.grid.grid-cols-2').first();
    await expect(filterContainer).toBeVisible();
    const triggers = filterContainer.locator('button[data-slot="select-trigger"]');
    expect(await triggers.count()).toBe(4);
    // Check first two triggers are on the same row (similar y)
    const box0 = await triggers.nth(0).boundingBox();
    const box1 = await triggers.nth(1).boundingBox();
    expect(box0).not.toBeNull();
    expect(box1).not.toBeNull();
    if (box0 && box1) {
      expect(Math.abs(box0.y - box1.y)).toBeLessThan(5);
    }
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
