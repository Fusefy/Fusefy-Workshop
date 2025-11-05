#!/usr/bin/env python3
"""
Simple test runner for development that works with SQLite and avoids PostgreSQL dependencies.
This script provides quick test commands that work with the current setup.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔧 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print(f"✅ {description} - SUCCESS")
    else:
        print(f"❌ {description} - FAILED (exit code: {result.returncode})")
    
    return result.returncode == 0


def main():
    """Run the test suite with working configuration."""
    
    print("🧪 Claims Reimbursement System - Development Test Runner")
    print("=" * 65)
    print("This runner uses configurations that work with SQLite development setup")
    print()
    
    # Set environment variables
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    
    # Available commands
    commands = {
        "1": {
            "cmd": "pytest tests/unit/test_models.py -p no:postgresql --tb=short -v -k 'not async'",
            "desc": "Unit tests - Models (sync tests only)"
        },
        "2": {
            "cmd": "pytest tests/unit/test_schemas.py -p no:postgresql --tb=short -v -k 'not async'",
            "desc": "Unit tests - Schemas (sync tests only)"
        },
        "3": {
            "cmd": "pytest tests/unit/ -p no:postgresql --tb=short -k 'not async'",
            "desc": "All unit tests (sync only)"
        },
        "4": {
            "cmd": "pytest tests/ -p no:postgresql --tb=line -x --disable-warnings",
            "desc": "Quick test run (stop on first failure, minimal output)"
        },
        "5": {
            "cmd": "pytest tests/unit/test_models.py::TestClaimModel::test_claim_status_enum -p no:postgresql -v",
            "desc": "Single test example"
        },
        "6": {
            "cmd": "pytest --collect-only -q",
            "desc": "List all available tests"
        }
    }
    
    print("Available test commands:")
    for key, info in commands.items():
        print(f"  {key}. {info['desc']}")
    
    print("\nOr run directly:")
    print("  pytest tests/unit/ -p no:postgresql --tb=short")
    print("  pytest tests/ -p no:postgresql -x --disable-warnings")
    print()
    
    choice = input("Enter choice (1-6) or press Enter for option 3: ").strip()
    if not choice:
        choice = "3"
    
    if choice in commands:
        success = run_command(commands[choice]["cmd"], commands[choice]["desc"])
        sys.exit(0 if success else 1)
    else:
        print("Invalid choice. Running default unit tests...")
        success = run_command(commands["3"]["cmd"], commands["3"]["desc"])
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()