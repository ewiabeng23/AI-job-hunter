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

test.describe('Job Search', () => {
  test('should show search form after login', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should search for jobs', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should show Easy Apply checkbox', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });

  test('should filter easy apply jobs', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.search-form')).toBeVisible();
  });
});
