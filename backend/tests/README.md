# Testing Guide


# Single test
pytest tests/unit/test_schemas.py::TestClaimCreateSchema::test_claim_create_valid_data -p no:postgresql -v --disable-warnings

# All schema tests
pytest tests/unit/test_schemas.py -p no:postgresql --disable-warnings

# Quick unit tests
pytest tests/unit/ -p no:postgresql --tb=short --disable-warnings -k "not async"


## Quick Start

The simplest way to run tests is using pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output to see the flow
pytest -v

# Run with coverage
pytest --cov=src
```

## Running Specific Tests

### By File
```bash
# Run all claims API tests
pytest tests/api/test_claims.py

# Run all health check tests
pytest tests/api/test_health.py

# Run all model tests
pytest tests/unit/test_models.py

# Run all schema tests
pytest tests/unit/test_schemas.py
```

### By Test Class or Function
```bash
# Run specific test class
pytest tests/api/test_claims.py::TestClaimsAPI

# Run specific test method
pytest tests/api/test_claims.py::TestClaimsAPI::test_create_claim

# Run specific test function
pytest tests/api/test_health.py::test_health_check_basic
```

### By Test Pattern
```bash
# Run all tests containing 'create' in the name
pytest -k "test_create"

# Run all tests containing 'claim' in the name
pytest -k "claim"

# Run tests that match multiple patterns
pytest -k "test_create or test_update"
```

## Test Categories

### Unit Tests (Fast)
```bash
# Run only unit tests
pytest tests/unit/

# Run unit tests with coverage
pytest tests/unit/ --cov=src
```

### Integration Tests (Slower)
```bash
# Run only integration tests
pytest tests/api/

# Run integration tests with verbose output
pytest tests/api/ -v
```

## Useful Options

### Debugging and Output
```bash
# Stop on first failure
pytest -x

# Show detailed test output
pytest -v

# Show even more detailed output
pytest -vv

# Show local variables on failures
pytest -l

# Drop into debugger on failures
pytest --pdb
```

### Coverage Reporting
```bash
# Basic coverage report
pytest --cov=src

# Coverage with missing lines
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Coverage with fail threshold
pytest --cov=src --cov-fail-under=80
```

### Test Selection
```bash
# Run last failed tests only
pytest --lf

# Run failed tests first, then others
pytest --ff

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

## Test Structure

```
tests/
├── conftest.py              # Fixtures and configuration
├── api/                     # Integration tests
│   ├── test_claims.py       # Claims API endpoints
│   └── test_health.py       # Health check endpoints
└── unit/                    # Unit tests
    ├── test_models.py       # Database models
    └── test_schemas.py      # Pydantic schemas
```

## Available Fixtures

The test suite provides several fixtures in `conftest.py`:

- `test_db_session` - Database session for testing
- `test_client` - FastAPI test client
- `async_client` - Async HTTP client
- `sample_claim_data` - Sample claim data
- `sample_claim_in_db` - Sample claim in database
- `multiple_claims_in_db` - Multiple test claims

## Example Test Commands

### Development Workflow
```bash
# Quick check - run tests and stop on first failure
pytest -x

# Develop specific feature - run related tests with verbose output
pytest tests/api/test_claims.py -v

# Check test coverage for specific file
pytest tests/api/test_claims.py --cov=src.api.claims --cov-report=term-missing

# Run all tests with coverage report
pytest --cov=src --cov-report=html
```

### CI/CD Pipeline
```bash
# Full test suite with coverage and XML reports
pytest --cov=src --cov-report=xml --cov-fail-under=80 --junitxml=test-results.xml
```

## Common Test Patterns

### Testing API Endpoints
```python
def test_create_claim(test_client, sample_claim_data):
    response = test_client.post("/api/v1/claims/", json=sample_claim_data)
    assert response.status_code == 201
    assert response.json()["patient_name"] == sample_claim_data["patient_name"]
```

### Testing Database Operations
```python
async def test_claim_creation(test_db_session, sample_claim_data):
    claim = Claim(**sample_claim_data)
    test_db_session.add(claim)
    await test_db_session.commit()
    assert claim.id is not None
```

### Testing Validation
```python
def test_invalid_claim_data(test_client):
    invalid_data = {"patient_name": "John Doe"}  # Missing required fields
    response = test_client.post("/api/v1/claims/", json=invalid_data)
    assert response.status_code == 422
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running pytest from the backend directory
2. **Database Errors**: Tests use in-memory SQLite, no setup needed
3. **Async Errors**: Use `pytest-asyncio` for async test functions
4. **Fixture Errors**: Check `conftest.py` for available fixtures

### Debug Mode
```bash
# Run with Python warnings enabled
pytest -W error

# Show deprecation warnings
pytest -W ignore::DeprecationWarning

# Run in debug mode with print statements
pytest -s
```

## Performance

- Unit tests should run in < 1 second each
- Integration tests may take 2-5 seconds each
- Full test suite should complete in < 30 seconds
- Use `pytest -x` for faster feedback during development

## Best Practices

1. **Keep tests simple** - One assertion per test when possible
2. **Use descriptive names** - `test_create_claim_with_valid_data`
3. **Use fixtures** - Leverage `conftest.py` fixtures for setup
4. **Test edge cases** - Invalid data, missing fields, etc.
5. **Mock external services** - Don't make real API calls in tests
6. **Keep tests isolated** - Each test should be independent