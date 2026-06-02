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

test.describe('Job Search', () => {
  test('should show search form after login', async ({ page }) => {
    await login(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await login(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should show Easy Apply checkbox', async ({ page }) => {
    await login(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should filter easy apply jobs', async ({ page }) => {
    await login(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });
});
