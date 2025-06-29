import { chromium, FullConfig } from '@playwright/test';
import { spawn } from 'child_process';
import { promisify } from 'util';
import { exec } from 'child_process';

const execAsync = promisify(exec);

/**
 * Global setup for E2E tests
 * - Ensures database is seeded
 * - Creates a shared authentication state
 */
async function globalSetup(config: FullConfig) {
  // Check if database is running
  try {
    await execAsync('docker ps | grep postgres');
  } catch (error) {
    console.log('Starting PostgreSQL database...');
    spawn('docker-compose', ['up', '-d', 'postgres'], { stdio: 'inherit' });
    
    // Wait for database to start
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  
  // Seed database with test data if needed
  try {
    console.log('Seeding database with test data...');
    await execAsync('cd scripts && python3 seed-database.py --test');
  } catch (error) {
    console.error('Failed to seed database:', error);
  }
  
  // Setup shared authentication state
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Go to the login page
    await page.goto(`${baseURL}/auth/signin`);
    
    // Fill in login form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    
    // Click sign in and wait for navigation
    await Promise.all([
      page.click('button:has-text("Sign In")'),
      page.waitForNavigation({ waitUntil: 'networkidle' })
    ]);
    
    // Save signed-in state
    await page.context().storageState({ path: 'playwright/.auth/user.json' });
  } catch (error) {
    console.error('Failed to setup authentication:', error);
  } finally {
    await browser.close();
  }
}

export default globalSetup;