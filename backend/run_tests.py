#!/usr/bin/env python3
"""
Simple test runner for the Claims Reimbursement System.

Basic pytest commands:
    # Run all tests
    pytest

    # Run specific file
    pytest tests/api/test_claims.py

    # Run specific test
    pytest tests/api/test_claims.py::TestClaimsAPI::test_create_claim

    # Run with verbose output
    pytest -v

    # Run with coverage
    pytest --cov=src

For more examples, see tests/README.md
"""

import sys


def main():
    """Show simple pytest usage examples."""
    print("🧪 Claims Reimbursement System - Simple Test Commands")
    print("=" * 60)
    print()
    print("Basic Commands:")
    print("  pytest                              # Run all tests")
    print("  pytest -v                           # Run with verbose output")
    print("  pytest --cov=src                    # Run with coverage")
    print("  pytest tests/api/                   # Run API tests only")
    print("  pytest tests/unit/                  # Run unit tests only")
    print()
    print("Specific Tests:")
    print("  pytest tests/api/test_claims.py     # Run claims API tests")
    print("  pytest tests/unit/test_models.py    # Run model tests")
    print("  pytest tests/unit/test_schemas.py   # Run schema tests")
    print()
    print("Advanced:")
    print("  pytest -k 'test_create'             # Run tests matching pattern")
    print("  pytest -x                           # Stop on first failure")
    print("  pytest --lf                         # Run last failed tests")
    print("  pytest --cov=src --cov-report=html  # Generate HTML coverage")
    print()
    print("📖 For detailed examples, see tests/README.md")


if __name__ == "__main__":
    main()