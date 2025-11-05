# Quick Start Guide

## Setup Instructions

1. **Navigate to the correct directory**:
   ```bash
   cd d:\python\claim-agent\backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**:
   ```bash
   # Run all tests
   pytest

   # Run specific tests with verbose output
   pytest tests/api/test_health.py -v

   # Run with coverage
   pytest --cov=src
   ```

## If you're in a different project

If you're working on a different project (like `D:\python\ai-foudary2\backend`), you'll need:

1. **Create a similar structure**:
   - Move your test files to match our structure
   - Update imports to match your project structure
   - Install the required dependencies

2. **Fix common issues**:
   - Install missing packages: `pip install fastapi uvicorn pytest pytest-asyncio faker`
   - Check your import paths in conftest.py
   - Make sure your main application doesn't import packages you haven't installed

## Current Status

Your Claims Reimbursement System is ready with:
- ✅ Simple pytest commands
- ✅ Comprehensive test structure
- ✅ Detailed README in tests/ folder
- ✅ All dependencies listed in requirements.txt

Just install the dependencies and you're good to go!