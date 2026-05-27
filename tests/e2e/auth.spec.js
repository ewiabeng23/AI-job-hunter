import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {

  test('should show login page by default', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Job Hunter/);
    await expect(page.locator('h1')).toContainText('Job Hunter');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'wrong@email.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    await expect(page.locator('.error-message')).toBeVisible({ timeout: 10000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL);
    await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Search Jobs')).toBeVisible({ timeout: 15000 });
  });

  test('should navigate to signup page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Sign up');
    await expect(page.url()).toContain('/signup');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL);
    await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Search Jobs')).toBeVisible({ timeout: 15000 });
    
    // Logout
    await page.click('text=Logout');
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10000 });
  });

});
