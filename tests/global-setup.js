import { request } from '@playwright/test';
import fs from 'fs';

export default async function globalSetup() {
  const context = await request.newContext({
    ignoreHTTPSErrors: true
  });
  
  const response = await context.post(
    'https://jobhunter.wigsbydiko.co.uk/api/auth/login',
    {
      data: {
        email: process.env.TEST_USER_EMAIL,
        password: process.env.TEST_USER_PASSWORD
      }
    }
  );

  if (!response.ok()) {
    throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
  }

  const { access_token, user } = await response.json();
  
  // Save token to a file for tests to use
  fs.writeFileSync('auth-token.json', JSON.stringify({ 
    token: access_token, 
    user 
  }));

  // Save storage state
  await context.storageState({ path: 'auth.json' });
  console.log('✅ Global setup: logged in as', user.email);
}
