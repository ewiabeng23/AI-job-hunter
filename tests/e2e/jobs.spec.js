import { test, expect } from '@playwright/test';

// Helper to login
async function login(page) {
  await page.goto('/');
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL);
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page.locator('text=🔍 Search Jobs')).toBeVisible({ timeout: 15000 });
}

test.describe('Job Search', () => {

  test('should show search form after login', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=Find Your Dream Job')).toBeVisible();
    await expect(page.locator('text=Job Title')).toBeVisible();
    await expect(page.locator('text=Location')).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await login(page);
    await page.fill('input[placeholder="e.g., DevOps Engineer"]', 'DevOps Engineer');
    await page.fill('input[placeholder="e.g., London, UK"]', 'London');
    await page.click('text=🔍 Search Jobs');
    await expect(page.locator('text=Found')).toBeVisible({ timeout: 30000 });
  });

  test('should show Easy Apply checkbox', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=Easy Apply only')).toBeVisible();
  });

  test('should filter easy apply jobs', async ({ page }) => {
    await login(page);
    await page.check('input[type="checkbox"]');
    await page.fill('input[placeholder="e.g., DevOps Engineer"]', 'DevOps');
    await page.fill('input[placeholder="e.g., London, UK"]', 'London');
    await page.click('text=🔍 Search Jobs');
    await expect(page.locator('text=Found')).toBeVisible({ timeout: 30000 });
  });

});
