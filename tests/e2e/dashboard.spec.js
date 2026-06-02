import { test, expect } from '@playwright/test';

async function login(page) {
  await page.goto('/');
  await page.waitForSelector('input[type="email"]', { timeout: 10000 });
  await page.click('input[type="email"]');
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL);
  await page.click('input[type="password"]');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page.locator('.tabs')).toBeVisible({ timeout: 20000 });
}

test.describe('Dashboard Navigation', () => {
  test('should show all tabs', async ({ page }) => {
    await login(page);
    await expect(page.locator('.tab')).toHaveCount(4);
  });

  test('should navigate to My CVs tab', async ({ page }) => {
    await login(page);
    await page.click('text=My CVs');
    await expect(page.locator('.tab.active')).toContainText('CV');
  });

  test('should navigate to Applications tab', async ({ page }) => {
    await login(page);
    await page.click('text=Applications');
    await expect(page.locator('.tab.active')).toContainText('Application');
  });

  test('should show user info in header', async ({ page }) => {
    await login(page);
    await expect(page.locator('.dashboard')).toBeVisible();
  });
});
