@echo off
REM Simple pytest commands for Windows
REM Use pytest directly for the simplest experience

echo 🧪 Claims Reimbursement System - Simple Test Commands
echo ==========================================================
echo.
echo Basic Commands:
echo   pytest                              # Run all tests
echo   pytest -v                           # Run with verbose output
echo   pytest --cov=src                    # Run with coverage
echo   pytest tests/api/                   # Run API tests only
echo   pytest tests/unit/                  # Run unit tests only
echo.
echo Specific Tests:
echo   pytest tests/api/test_claims.py     # Run claims API tests
echo   pytest tests/unit/test_models.py    # Run model tests
echo   pytest tests/unit/test_schemas.py   # Run schema tests
echo.
echo Advanced:
echo   pytest -k "test_create"             # Run tests matching pattern
echo   pytest -x                           # Stop on first failure  
echo   pytest --lf                         # Run last failed tests
echo   pytest --cov=src --cov-report=html  # Generate HTML coverage
echo.
echo 📖 For detailed examples, see tests/README.md