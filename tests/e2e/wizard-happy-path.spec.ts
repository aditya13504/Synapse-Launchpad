import { test, expect } from '@playwright/test';

test.describe('Wizard Happy Path', () => {
  test('should complete the entire wizard flow from login to campaign generation', async ({ page }) => {
    // Step 1: Login
    await page.goto('/auth/signin');
    
    // Fill in login credentials
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    // Click login button and wait for navigation
    await Promise.all([
      page.click('button:has-text("Sign In")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Verify successful login by checking for dashboard elements
    await expect(page).toHaveURL('/wizard');
    await expect(page.locator('h1:has-text("Partnership Wizard")')).toBeVisible();
    
    // Step 2: Business Goals Input
    // Verify we're on the business goals step
    await expect(page.locator('text=Define Your Business Goals')).toBeVisible();
    
    // Select primary objective
    await page.click('label:has-text("Accelerate Growth")');
    
    // Select target markets
    await page.click('button:has-text("Enterprise (B2B)")');
    await page.click('button:has-text("SaaS")');
    
    // Select growth stage
    await page.click('label:has-text("Series A")');
    
    // Enter budget
    await page.fill('input[type="number"]', '25000');
    
    // Select timeline
    await page.click('label:has-text("3-6 months")');
    
    // Select success metrics
    await page.click('button:has-text("Revenue Growth")');
    await page.click('button:has-text("Market Share")');
    
    // Submit form and wait for navigation to next step
    await Promise.all([
      page.click('button:has-text("Find Partners")'),
      page.waitForResponse(response => 
        response.url().includes('/api/partners') && 
        response.status() === 200
      )
    ]);
    
    // Step 3: Partner Recommendations
    // Verify we're on the partner recommendations step
    await expect(page.locator('text=Partner Recommendations')).toBeVisible();
    
    // Wait for recommendations to load
    await page.waitForSelector('.glass-morphism', { state: 'visible' });
    
    // Select the first partner
    const firstPartner = page.locator('.glass-morphism').first();
    await firstPartner.click();
    
    // Verify partner selection by checking for selected state
    await expect(firstPartner).toHaveClass(/ring-2/);
    
    // Click Generate Campaign button
    await Promise.all([
      page.click('button:has-text("Generate Campaign")'),
      page.waitForResponse(response => 
        response.url().includes('/api/campaigns') && 
        response.status() === 200
      )
    ]);
    
    // Step 4: Campaign Editor
    // Verify we're on the campaign editor step
    await expect(page.locator('text=Campaign Generation')).toBeVisible();
    
    // Wait for campaign data to load
    await page.waitForSelector('text=Campaign Brief', { state: 'visible' });
    
    // Verify campaign JSON is shown
    const campaignJson = page.locator('pre').first();
    await expect(campaignJson).toBeVisible();
    
    // Verify campaign contains expected data
    const campaignText = await campaignJson.textContent();
    expect(campaignText).toContain('campaign_id');
    expect(campaignText).toContain('campaign_brief');
    expect(campaignText).toContain('channel_mix_plan');
    
    // Verify success message
    await expect(page.locator('text=Campaign generated successfully')).toBeVisible();
    
    // Take a screenshot of the final state
    await page.screenshot({ path: 'wizard-complete.png' });
  });
});