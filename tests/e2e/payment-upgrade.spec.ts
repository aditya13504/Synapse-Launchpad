import { test, expect } from '@playwright/test';

test.describe('Payment Upgrade Flow', () => {
  test('should upgrade from free to Pro plan using Stripe test card', async ({ page }) => {
    // Step 1: Login
    await page.goto('/auth/signin');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    await Promise.all([
      page.click('button:has-text("Sign In")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Step 2: Navigate to pricing page
    await page.goto('/pricing');
    
    // Verify we're on the pricing page
    await expect(page.locator('h1:has-text("Choose Your Growth Plan")')).toBeVisible();
    
    // Step 3: Select Pro plan
    // First, ensure we're on monthly billing
    await page.click('button:has-text("Monthly")');
    
    // Find the Pro plan card and click its button
    const proCard = page.locator('.card', { hasText: 'Pro' });
    await expect(proCard).toBeVisible();
    
    // Click the "Get Started" button on the Pro plan
    await Promise.all([
      proCard.locator('button:has-text("Get Started")').click(),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Step 4: Verify redirect to Stripe checkout
    await expect(page.url()).toContain('checkout.stripe.com');
    
    // Step 5: Fill in Stripe test card details
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
    
    // Step 6: Submit payment
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Step 7: Verify successful upgrade
    // We should be redirected back to the dashboard
    await expect(page.url()).toContain('/dashboard');
    
    // Check for success message
    await expect(page.locator('text=Subscription successful')).toBeVisible();
    
    // Step 8: Verify Pro features are unlocked
    // Navigate to the wizard to check for Pro features
    await page.goto('/wizard');
    
    // Check for Pro badge
    await expect(page.locator('text=Pro Plan')).toBeVisible();
    
    // Verify unlimited partner recommendations are available
    await page.click('text=Business Goals');
    await page.click('text=Partner Recommendations');
    
    // In the free plan, only 3 recommendations are shown
    // In Pro, more than 3 should be visible
    const recommendations = page.locator('.glass-morphism');
    await expect(recommendations).toHaveCount({ min: 4 });
    
    // Take a screenshot of the Pro features
    await page.screenshot({ path: 'pro-features-unlocked.png' });
  });
});