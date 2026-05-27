import { test, expect } from '@playwright/test';

async function login(page) {
  await page.goto('/');
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL);
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Search Jobs')).toBeVisible({ timeout: 15000 });
}

test.describe('Dashboard Navigation', () => {

  test('should show all tabs', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=Search Jobs')).toBeVisible();
    await expect(page.locator('text=My CVs')).toBeVisible();
    await expect(page.locator('text=Applications')).toBeVisible();
    await expect(page.locator('text=Interview Prep')).toBeVisible();
  });

  test('should navigate to My CVs tab', async ({ page }) => {
    await login(page);
    await page.click('text=My CVs');
    await expect(page.locator('text=Upload your master CV')).toBeVisible();
  });

  test('should navigate to Applications tab', async ({ page }) => {
    await login(page);
    await page.click('text=Applications');
    await expect(page.locator('text=My Applications')).toBeVisible();
  });

  test('should show user info in header', async ({ page }) => {
    await login(page);
    await expect(page.locator('.tier-badge')).toBeVisible();
    await expect(page.locator('text=PRO')).toBeVisible();
  });

});
