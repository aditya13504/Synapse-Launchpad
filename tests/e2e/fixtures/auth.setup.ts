import { test as setup, expect } from '@playwright/test';

// Store signed-in state
const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Go to the login page
  await page.goto('/auth/signin');
  
  // Fill in login form
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  
  // Click sign in and wait for navigation
  await Promise.all([
    page.click('button:has-text("Sign In")'),
    page.waitForNavigation({ waitUntil: 'networkidle' })
  ]);
  
  // Verify we're logged in
  await expect(page.locator('text=Dashboard')).toBeVisible();
  
  // Save signed-in state
  await page.context().storageState({ path: authFile });
});