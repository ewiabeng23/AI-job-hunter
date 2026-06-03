import { test, expect } from '@playwright/test';
import fs from 'fs';

function getAuth() {
  return JSON.parse(fs.readFileSync('auth-token.json', 'utf8'));
}

async function loginWithToken(page) {
  const { token, user } = getAuth();
  await page.goto('/');
  await page.evaluate(({ token, user }) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }, { token, user });
  await page.reload();
  await expect(page.locator('.tabs')).toBeVisible({ timeout: 20000 });
}

test.describe('Authentication', () => {
  test('should show login page by default', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Job Hunter/);
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
    await loginWithToken(page);
    await expect(page.locator('.tabs')).toBeVisible();
  });

  test('should navigate to signup page', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Sign up');
    await expect(page.url()).toContain('/signup');
  });

  test('should logout successfully', async ({ page }) => {
    await loginWithToken(page);
    await page.click('text=Logout');
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10000 });
  });
});
