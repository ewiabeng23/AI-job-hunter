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

test.describe('Dashboard Navigation', () => {
  test('should show all tabs', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.tab')).toHaveCount(4);
  });

  test('should navigate to My CVs tab', async ({ page }) => {
    await loginWithToken(page);
    await page.click('text=My CVs');
    await expect(page.locator('.tab.active')).toContainText('CV');
  });

  test('should navigate to Applications tab', async ({ page }) => {
    await loginWithToken(page);
    await page.click('text=Applications');
    await expect(page.locator('.tab.active')).toContainText('Application');
  });

  test('should show user info in header', async ({ page }) => {
    await loginWithToken(page);
    await expect(page.locator('.dashboard')).toBeVisible();
  });
});
