# End-to-End Tests for Synapse LaunchPad

This directory contains Playwright end-to-end tests for the Synapse LaunchPad application.

## 🧪 Test Suites

### 1. Wizard Happy Path
Tests the complete user journey from login to campaign generation:
- Login
- Business goals input
- Partner recommendations
- Campaign generation
- Verification of generated campaign

### 2. Payment Upgrade
Tests the payment flow for upgrading from free to Pro plan:
- Login
- Navigate to pricing page
- Select Pro plan
- Complete Stripe checkout with test card
- Verify Pro features are unlocked

### 3. Authentication
Tests login, logout, and authentication error handling.

### 4. Dashboard
Tests dashboard functionality and navigation.

## 🚀 Running Tests

### Prerequisites
- Node.js 18+
- pnpm 8+
- Docker (for PostgreSQL)

### Installation
```bash
# Install dependencies
pnpm install

# Install Playwright browsers
npx playwright install --with-deps
```

### Running Tests
```bash
# Run all tests
pnpm test:e2e

# Run with UI
pnpm test:e2e:ui

# Run specific test file
npx playwright test wizard-happy-path.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium

# View test report
pnpm test:e2e:report
```

## 📊 Test Reports

Test reports are generated in HTML, JSON, and JUnit XML formats:
- HTML: `playwright-report/`
- JSON: `test-results/e2e-results.json`
- XML: `test-results/e2e-results.xml`

In CI/CD pipelines, these reports are uploaded as artifacts and can be viewed in the GitHub Actions UI or in the 21st.dev dashboard.

## 🔄 CI/CD Integration

Tests are automatically run in the CI/CD pipeline:
- On every push to `main` and `develop` branches
- On every pull request to `main`

### CI/CD Workflow
1. Checkout code
2. Setup Node.js and dependencies
3. Install Playwright browsers
4. Start PostgreSQL and seed test database
5. Build application
6. Run Playwright tests
7. Upload test results as artifacts
8. Deploy if all tests pass (for `main` branch)

## 📝 Writing Tests

### Best Practices
1. **Use page objects**: Encapsulate page interactions in reusable functions
2. **Avoid flaky selectors**: Use data-testid attributes when possible
3. **Handle async properly**: Use `await` for all async operations
4. **Add proper assertions**: Verify expected outcomes, not just navigation
5. **Keep tests independent**: Each test should be able to run in isolation

### Example Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should perform specific action', async ({ page }) => {
    // Arrange - set up test conditions
    await page.goto('/some-page');
    
    // Act - perform the action being tested
    await page.click('button:has-text("Do Something")');
    
    // Assert - verify the expected outcome
    await expect(page.locator('.result')).toContainText('Success');
  });
});
```

## 🔧 Configuration

The test configuration is defined in `playwright.config.ts` and includes:
- Browser configurations (Chrome, Firefox, Safari, mobile browsers)
- Timeouts and retry settings
- Screenshot and video capture settings
- Reporter configuration
- Web server setup

## 🚨 Troubleshooting

### Common Issues

1. **Tests failing due to timing issues**
   - Increase timeouts in the config
   - Use more reliable wait conditions (waitForSelector, waitForResponse)

2. **Selectors not working**
   - Check if the element is in an iframe
   - Verify the element is visible and not covered
   - Try different selector strategies (text, role, testid)

3. **Authentication issues**
   - Check if the auth state is being properly saved and loaded
   - Verify the test user exists in the test database

### Debugging Tips

1. **Use UI mode**: `pnpm test:e2e:ui`
2. **Add screenshots**: `await page.screenshot({ path: 'debug.png' });`
3. **Enable tracing**: Set `trace: 'on'` in the config
4. **Check console logs**: `page.on('console', msg => console.log(msg.text()));`