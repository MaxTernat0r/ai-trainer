import { test, expect } from '@playwright/test';
import { loginAsTestUser, expectNoHorizontalScroll } from './helpers/auth';

const PUBLIC_PAGES = [
  { path: '/', name: 'landing' },
  { path: '/login', name: 'login' },
  { path: '/register', name: 'register' },
];

const PRIVATE_PAGES = [
  { path: '/dashboard', name: 'dashboard' },
  { path: '/workouts', name: 'workouts' },
  { path: '/nutrition', name: 'nutrition' },
  { path: '/chat', name: 'chat' },
  { path: '/exercises', name: 'exercises' },
  { path: '/analytics', name: 'analytics' },
  { path: '/profile', name: 'profile' },
];

test.describe('Public pages mobile layout', () => {
  for (const p of PUBLIC_PAGES) {
    test(`${p.name} fits viewport without horizontal scroll`, async ({ page }, testInfo) => {
      await page.goto(p.path);
      await page.waitForLoadState('networkidle');
      await expectNoHorizontalScroll(page);
      await page.screenshot({
        path: `test-results/screenshots/${testInfo.project.name}-${p.name}.png`,
        fullPage: true,
      });
    });
  }
});

test.describe('Private pages mobile layout', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTestUser(page);
  });

  for (const p of PRIVATE_PAGES) {
    test(`${p.name} fits viewport without horizontal scroll`, async ({ page }, testInfo) => {
      await page.goto(p.path);
      await page.waitForLoadState('networkidle');
      await expectNoHorizontalScroll(page);
      await page.screenshot({
        path: `test-results/screenshots/${testInfo.project.name}-${p.name}.png`,
        fullPage: true,
      });
    });
  }
});

test.describe('Critical mobile interactions', () => {
  test('chat sidebar opens via Sheet on mobile', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
    const menuButton = page.getByRole('button', { name: /диалог/i });
    await expect(menuButton).toBeVisible();
    await menuButton.click();
    await expect(page.locator('[data-slot="sheet-content"]')).toBeVisible();
  });

  test('dashboard tab bar visible above safe area', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const tabBar = page.locator('nav.fixed').filter({ hasText: 'Главная' }).first();
    await expect(tabBar).toBeVisible();
    const box = await tabBar.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      const viewport = page.viewportSize();
      expect(viewport).not.toBeNull();
      if (viewport) {
        expect(box.y + box.height).toBeLessThanOrEqual(viewport.height);
      }
    }
  });
});
