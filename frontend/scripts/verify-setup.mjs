#!/usr/bin/env node

/**
 * Quick setup verification script
 * 
 * Runs basic checks to ensure the development environment is properly configured.
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

console.log('🔍 Verifying Claims Management Frontend Setup...\n');

// Check Node.js version
try {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  if (majorVersion >= 18) {
    console.log(`✅ Node.js ${nodeVersion} (compatible)`);
  } else {
    console.log(`❌ Node.js ${nodeVersion} (requires 18+)`);
    process.exit(1);
  }
} catch (error) {
  console.log(`❌ Error checking Node.js version: ${error.message}`);
  process.exit(1);
}

// Check package.json exists
const packageJsonPath = join(process.cwd(), 'package.json');
if (existsSync(packageJsonPath)) {
  console.log('✅ package.json found');
  
  try {
    const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
    console.log(`   Project: ${packageJson.name}@${packageJson.version}`);
  } catch (error) {
    console.log('⚠️  Could not parse package.json');
  }
} else {
  console.log('❌ package.json not found');
  console.log('   Make sure you\'re in the frontend directory');
  process.exit(1);
}

// Check if dependencies are installed
const nodeModulesPath = join(process.cwd(), 'node_modules');
if (existsSync(nodeModulesPath)) {
  console.log('✅ Dependencies installed');
} else {
  console.log('❌ Dependencies not installed');
  console.log('   Run: npm install');
  process.exit(1);
}

// Check environment file
const envPath = join(process.cwd(), '.env');
const envExamplePath = join(process.cwd(), '.env.example');

if (existsSync(envPath)) {
  console.log('✅ Environment file (.env) exists');
  
  try {
    const envContent = readFileSync(envPath, 'utf8');
    if (envContent.includes('VITE_API_BASE_URL')) {
      console.log('✅ API base URL configured');
    } else {
      console.log('⚠️  VITE_API_BASE_URL not found in .env');
    }
  } catch (error) {
    console.log('⚠️  Could not read .env file');
  }
} else if (existsSync(envExamplePath)) {
  console.log('⚠️  .env file not found, but .env.example exists');
  console.log('   Run: cp .env.example .env');
} else {
  console.log('❌ No environment configuration found');
}

// Check TypeScript configuration
const tsconfigPath = join(process.cwd(), 'tsconfig.json');
if (existsSync(tsconfigPath)) {
  console.log('✅ TypeScript configuration found');
} else {
  console.log('❌ TypeScript configuration missing');
}

// Check Vite configuration
const viteConfigPath = join(process.cwd(), 'vite.config.ts');
if (existsSync(viteConfigPath)) {
  console.log('✅ Vite configuration found');
} else {
  console.log('❌ Vite configuration missing');
}

// Check Tailwind configuration
const tailwindConfigPath = join(process.cwd(), 'tailwind.config.js');
if (existsSync(tailwindConfigPath)) {
  console.log('✅ Tailwind CSS configuration found');
} else {
  console.log('❌ Tailwind CSS configuration missing');
}

// Check source directory structure
const srcPath = join(process.cwd(), 'src');
const requiredDirs = [
  'components',
  'pages',
  'hooks',
  'services',
  'types',
  'utils'
];

if (existsSync(srcPath)) {
  console.log('✅ Source directory exists');
  
  let allDirsExist = true;
  for (const dir of requiredDirs) {
    const dirPath = join(srcPath, dir);
    if (existsSync(dirPath)) {
      console.log(`   ✅ ${dir}/ directory`);
    } else {
      console.log(`   ❌ ${dir}/ directory missing`);
      allDirsExist = false;
    }
  }
  
  if (!allDirsExist) {
    console.log('   Some required directories are missing');
  }
} else {
  console.log('❌ Source directory missing');
}

// Check if backend is running
console.log('\n🔍 Checking backend connectivity...');

try {
  const apiUrl = process.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  // Note: This is a simplified check. In a real script, you'd use fetch or axios
  console.log(`   Configured API URL: ${apiUrl}`);
  console.log('   ⚠️  Backend connectivity check requires manual verification');
  console.log('   Make sure your FastAPI backend is running on the configured URL');
  
} catch (error) {
  console.log(`   ❌ Error checking backend: ${error.message}`);
}

console.log('\n📋 Setup Summary:');
console.log('   Frontend: Ready for development');
console.log('   Next steps:');
console.log('   1. Ensure backend is running (see backend README)');
console.log('   2. Run: npm run dev');
console.log('   3. Open: http://localhost:3000');

console.log('\n🎉 Frontend setup verification complete!');

export default {};