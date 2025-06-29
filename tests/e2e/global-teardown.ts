import { FullConfig } from '@playwright/test';
import { promisify } from 'util';
import { exec } from 'child_process';

const execAsync = promisify(exec);

/**
 * Global teardown for E2E tests
 * - Cleans up resources after tests
 */
async function globalTeardown(config: FullConfig) {
  // Clean up resources if needed
  if (process.env.CI) {
    try {
      // In CI, we might want to stop services to free resources
      await execAsync('docker-compose down postgres');
    } catch (error) {
      console.error('Failed to stop services:', error);
    }
  }
}

export default globalTeardown;