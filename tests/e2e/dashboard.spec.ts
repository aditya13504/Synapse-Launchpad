import { test, expect } from '@playwright/test';

// Use the authentication state from auth.setup.ts
test.use({ storageState: 'playwright/.auth/user.json' });

test.describe('Dashboard', () => {
  test('should display dashboard with key metrics', async ({ page }) => {
    // Go to the dashboard
    await page.goto('/dashboard');
    
    // Verify dashboard elements
    await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
    
    // Check for metrics cards
    await expect(page.locator('text=Partner Matches')).toBeVisible();
    await expect(page.locator('text=Active Campaigns')).toBeVisible();
    await expect(page.locator('text=Partnership ROI')).toBeVisible();
    
    // Check for recent activity section
    await expect(page.locator('h2:has-text("Recent Activity")')).toBeVisible();
    
    // Check for navigation elements
    await expect(page.locator('a:has-text("Find Partners")')).toBeVisible();
    await expect(page.locator('a:has-text("Campaigns")')).toBeVisible();
  });
  
  test('should navigate to wizard from dashboard', async ({ page }) => {
    // Go to the dashboard
    await page.goto('/dashboard');
    
    // Click on Find Partners button
    await Promise.all([
      page.click('a:has-text("Find Partners")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Verify we're on the wizard page
    await expect(page).toHaveURL('/wizard');
    await expect(page.locator('h1:has-text("Partnership Wizard")')).toBeVisible();
  });
});