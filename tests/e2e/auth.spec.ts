import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should allow user to sign in', async ({ page }) => {
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
    
    // Verify successful login
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });
  
  test('should show error for invalid credentials', async ({ page }) => {
    // Go to the login page
    await page.goto('/auth/signin');
    
    // Fill in login form with invalid credentials
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Click sign in
    await page.click('button:has-text("Sign In")');
    
    // Verify error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible();
  });
  
  test('should allow user to sign out', async ({ page }) => {
    // Login first
    await page.goto('/auth/signin');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    await Promise.all([
      page.click('button:has-text("Sign In")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Click on user menu
    await page.click('button[aria-label="User menu"]');
    
    // Click sign out
    await Promise.all([
      page.click('button:has-text("Sign out")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Verify we're logged out and redirected to login page
    await expect(page).toHaveURL('/auth/signin');
  });
});