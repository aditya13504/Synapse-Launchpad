import { Page, expect } from '@playwright/test';

/**
 * Helper function to fill in the business goals form
 */
export async function fillBusinessGoalsForm(page: Page) {
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
  
  // Submit form
  await Promise.all([
    page.click('button:has-text("Find Partners")'),
    page.waitForResponse(response => 
      response.url().includes('/api/partners') && 
      response.status() === 200
    )
  ]);
}

/**
 * Helper function to select a partner from recommendations
 */
export async function selectPartner(page: Page, index: number = 0) {
  // Wait for recommendations to load
  await page.waitForSelector('.glass-morphism', { state: 'visible' });
  
  // Select the partner at the specified index
  const partners = page.locator('.glass-morphism');
  await partners.nth(index).click();
  
  // Verify partner selection
  await expect(partners.nth(index)).toHaveClass(/ring-2/);
  
  // Click Generate Campaign button
  await Promise.all([
    page.click('button:has-text("Generate Campaign")'),
    page.waitForResponse(response => 
      response.url().includes('/api/campaigns') && 
      response.status() === 200
    )
  ]);
}

/**
 * Helper function to fill Stripe payment details
 */
export async function fillStripePaymentDetails(page: Page) {
  // Wait for Stripe iframe to load
  const cardNumberFrame = page.frameLocator('iframe[name^="__privateStripeFrame"]').first();
  await cardNumberFrame.locator('[placeholder="Card number"]').fill('4242 4242 4242 4242');
  
  const cardExpiryFrame = page.frameLocator('iframe[name^="__privateStripeFrame"]').nth(1);
  await cardExpiryFrame.locator('[placeholder="MM / YY"]').fill('12 / 25');
  
  const cardCvcFrame = page.frameLocator('iframe[name^="__privateStripeFrame"]').nth(2);
  await cardCvcFrame.locator('[placeholder="CVC"]').fill('123');
  
  // Fill in name and email if required
  await page.fill('input#email', 'test@example.com');
  await page.fill('input#billingName', 'Test User');
}