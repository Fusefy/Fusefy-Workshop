"""
Pytest configuration and fixtures for the Claims Reimbursement System.

This module provides comprehensive fixtures for testing the FastAPI application,
including database setup, HTTP clients, mock data factories, and external service mocks.
"""

import asyncio
import os
import tempfile
import uuid
from decimal import Decimal
from typing import AsyncGenerator, Dict, Any, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import application components
from src.main import app
from src.config.database import get_db, db_config
from src.config.settings import settings
from src.models.base import Base
from src.models.claim import Claim, ClaimStatus
from src.schemas.claim import ClaimCreate, ClaimUpdate


# Initialize Faker for generating test data
fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    
    This fixture ensures that async tests have a consistent event loop
    throughout the test session, avoiding issues with multiple event loops.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """
    Create a test database engine using in-memory SQLite.
    
    This fixture provides a clean database engine for each test function,
    ensuring test isolation and fast execution. Uses SQLite's in-memory
    database for maximum speed.
    
    Yields:
        AsyncEngine: SQLAlchemy async engine connected to in-memory SQLite
    """
    # Create in-memory SQLite database for testing
    # Use StaticPool to ensure the same connection is reused
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    # Create all tables for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: dispose of the engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session with automatic transaction rollback.
    
    This fixture provides a database session that automatically rolls back
    all changes at the end of each test, ensuring test isolation and
    preventing data pollution between tests.
    
    Args:
        test_db_engine: The test database engine fixture
        
    Yields:
        AsyncSession: Database session that rolls back after test completion
    """
    # Create async session factory
    async_session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create a connection and begin a transaction
    async with test_db_engine.connect() as connection:
        # Begin a transaction that we can rollback
        transaction = await connection.begin()
        
        # Create session bound to this transaction
        session = async_session_factory(bind=connection)
        
        try:
            yield session
        finally:
            # Always rollback the transaction to ensure test isolation
            await session.close()
            await transaction.rollback()


@pytest.fixture(scope="function")
async def override_get_db(test_db_session: AsyncSession):
    """
    Override the database dependency for testing.
    
    This fixture replaces the application's database dependency with
    the test database session, ensuring all API calls use the test database.
    
    Args:
        test_db_session: The test database session fixture
    """
    async def _override_get_db():
        """Internal function to provide test database session."""
        yield test_db_session
    
    # Override the dependency
    app.dependency_overrides[get_db] = _override_get_db
    yield
    # Cleanup: remove the override
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_client(override_get_db) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI TestClient for synchronous HTTP testing.
    
    This fixture provides a test client that can make HTTP requests
    to the FastAPI application in tests. Uses the test database through
    the override_get_db fixture.
    
    Args:
        override_get_db: Database override fixture
        
    Yields:
        TestClient: FastAPI test client for making HTTP requests
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for asynchronous API testing.
    
    This fixture provides an async HTTP client that can make concurrent
    requests and test async endpoints. Preferred for integration tests
    that need to test async behavior.
    
    Args:
        override_get_db: Database override fixture
        
    Yields:
        AsyncClient: Async HTTP client for testing
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


# =============================================================================
# Mock Data Factory Fixtures
# =============================================================================

@pytest.fixture
def sample_claim_data() -> Dict[str, Any]:
    """
    Generate sample claim data for testing.
    
    This fixture creates realistic claim data using Faker,
    ensuring consistent test data structure while maintaining
    randomness for robust testing.
    
    Returns:
        Dict[str, Any]: Sample claim data dictionary
    """
    return {
        "claim_number": fake.bothify(text="CLM-####-????").upper(),
        "patient_name": fake.name(),
        "claim_amount": Decimal(fake.pydecimal(left_digits=4, right_digits=2, positive=True)),
        "status": fake.random_element(elements=list(ClaimStatus)),
        "document_url": f"gs://claims-bucket/{fake.file_name(extension='pdf')}",
        "raw_data": {
            "ocr_confidence": fake.pyfloat(min_value=0.8, max_value=1.0),
            "extracted_fields": {
                "patient_id": fake.bothify(text="PAT-#####"),
                "procedure_code": fake.bothify(text="###.##"),
                "diagnosis": fake.sentence(nb_words=4),
            }
        },
        "claim_metadata": {
            "source": fake.random_element(elements=["web_portal", "mobile_app", "email"]),
            "priority": fake.random_element(elements=["low", "normal", "high", "urgent"]),
            "submission_method": fake.random_element(elements=["electronic", "paper", "fax"]),
            "created_by": fake.email(),
        }
    }


@pytest.fixture
def sample_claim_create(sample_claim_data) -> ClaimCreate:
    """
    Create a ClaimCreate Pydantic model with sample data.
    
    This fixture converts sample claim data into a proper Pydantic
    model for testing API endpoints that expect ClaimCreate schemas.
    
    Args:
        sample_claim_data: Sample claim data fixture
        
    Returns:
        ClaimCreate: Pydantic model with sample claim data
    """
    # Remove fields that shouldn't be in ClaimCreate
    create_data = sample_claim_data.copy()
    return ClaimCreate(**create_data)


@pytest.fixture
def sample_claim_update() -> ClaimUpdate:
    """
    Create sample data for claim updates.
    
    This fixture generates partial update data for testing
    PATCH operations on claims.
    
    Returns:
        ClaimUpdate: Pydantic model with partial update data
    """
    return ClaimUpdate(
        status=ClaimStatus.HUMAN_REVIEW,
        claim_amount=Decimal("2500.75"),
        claim_metadata={
            "reviewer": fake.name(),
            "review_notes": fake.sentence(nb_words=10),
            "updated_at": fake.date_time().isoformat(),
        }
    )


@pytest.fixture
async def sample_claim_in_db(test_db_session: AsyncSession, sample_claim_data) -> Claim:
    """
    Create a sample claim record in the test database.
    
    This fixture creates and persists a claim in the test database,
    useful for testing GET, PATCH, and DELETE operations that require
    existing data.
    
    Args:
        test_db_session: Test database session
        sample_claim_data: Sample claim data
        
    Returns:
        Claim: The created claim model instance
    """
    # Create claim instance
    claim = Claim(**sample_claim_data)
    
    # Save to database
    test_db_session.add(claim)
    await test_db_session.commit()
    await test_db_session.refresh(claim)
    
    return claim


@pytest.fixture
async def multiple_claims_in_db(test_db_session: AsyncSession) -> list[Claim]:
    """
    Create multiple sample claims in the test database.
    
    This fixture creates several claims with different statuses and amounts
    for testing pagination, filtering, and bulk operations.
    
    Args:
        test_db_session: Test database session
        
    Returns:
        list[Claim]: List of created claim model instances
    """
    claims = []
    statuses = list(ClaimStatus)
    
    # Create 10 sample claims with different properties
    for i in range(10):
        claim_data = {
            "claim_number": fake.bothify(text=f"CLM-2024-{i:03d}"),
            "patient_name": fake.name(),
            "claim_amount": Decimal(fake.pydecimal(left_digits=3, right_digits=2, positive=True)),
            "status": statuses[i % len(statuses)],  # Cycle through statuses
            "document_url": f"gs://claims-bucket/claim-{i}.pdf",
            "raw_data": {"batch_id": f"batch-{i // 3}"},  # Group in batches
            "claim_metadata": {"priority": "normal" if i % 2 == 0 else "high"}
        }
        
        claim = Claim(**claim_data)
        test_db_session.add(claim)
        claims.append(claim)
    
    await test_db_session.commit()
    
    # Refresh all instances to get generated IDs
    for claim in claims:
        await test_db_session.refresh(claim)
    
    return claims


# =============================================================================
# Mock External Service Fixtures
# =============================================================================

@pytest.fixture
def mock_gcs_client():
    """
    Create a mock Google Cloud Storage client.
    
    This fixture provides a mock GCS client for testing operations
    that interact with Google Cloud Storage without actually
    connecting to GCS services.
    
    Returns:
        MagicMock: Mock GCS client with common methods
    """
    mock_client = MagicMock()
    
    # Mock bucket operations
    mock_bucket = MagicMock()
    mock_client.bucket.return_value = mock_bucket
    
    # Mock blob operations
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.upload_from_file.return_value = None
    mock_blob.download_to_file.return_value = None
    mock_blob.exists.return_value = True
    mock_blob.public_url = "https://storage.googleapis.com/bucket/file.pdf"
    
    return mock_client


@pytest.fixture
def mock_external_api():
    """
    Create mock for external API services.
    
    This fixture provides mocks for external services like
    OCR providers, payment processors, or notification services.
    
    Returns:
        MagicMock: Mock external API client
    """
    mock_api = MagicMock()
    
    # Mock OCR service response
    mock_api.extract_text.return_value = {
        "text": "Sample OCR extracted text",
        "confidence": 0.95,
        "fields": {
            "patient_name": "John Doe",
            "claim_amount": "1500.00",
            "procedure_code": "99213"
        }
    }
    
    # Mock notification service
    mock_api.send_notification.return_value = {
        "success": True,
        "message_id": fake.uuid4()
    }
    
    # Mock payment processor
    mock_api.process_payment.return_value = {
        "transaction_id": fake.uuid4(),
        "status": "completed",
        "amount": 1500.00
    }
    
    return mock_api


@pytest.fixture
def mock_async_external_service():
    """
    Create async mock for external services.
    
    This fixture provides async mocks for testing async operations
    that interact with external services.
    
    Returns:
        AsyncMock: Async mock external service
    """
    mock_service = AsyncMock()
    
    # Mock async OCR processing
    mock_service.process_document = AsyncMock(return_value={
        "status": "completed",
        "extracted_data": {
            "patient_name": fake.name(),
            "claim_amount": float(fake.pydecimal(left_digits=4, right_digits=2, positive=True)),
            "document_type": "medical_claim"
        },
        "processing_time_seconds": fake.pyfloat(min_value=1.0, max_value=5.0)
    })
    
    return mock_service


# =============================================================================
# Test Data Validation Fixtures
# =============================================================================

@pytest.fixture
def invalid_claim_data():
    """
    Generate invalid claim data for negative testing.
    
    This fixture provides various types of invalid data to test
    validation and error handling in the API endpoints.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of invalid data scenarios
    """
    return {
        "missing_required_fields": {
            "patient_name": fake.name(),
            # Missing claim_number and claim_amount
        },
        "invalid_claim_amount": {
            "claim_number": fake.bothify(text="CLM-####-????"),
            "patient_name": fake.name(),
            "claim_amount": -100.00,  # Negative amount
        },
        "invalid_status": {
            "claim_number": fake.bothify(text="CLM-####-????"),
            "patient_name": fake.name(),
            "claim_amount": Decimal("1500.00"),
            "status": "INVALID_STATUS",  # Not in ClaimStatus enum
        },
        "oversized_fields": {
            "claim_number": "X" * 100,  # Exceeds max length
            "patient_name": "Y" * 500,  # Exceeds max length
            "claim_amount": Decimal("1500.00"),
        },
        "invalid_json_fields": {
            "claim_number": fake.bothify(text="CLM-####-????"),
            "patient_name": fake.name(),
            "claim_amount": Decimal("1500.00"),
            "raw_data": "not_a_dict",  # Should be dict/JSON
        }
    }


# =============================================================================
# Performance Testing Fixtures
# =============================================================================

@pytest.fixture
def performance_timer():
    """
    Provide a simple performance timer for testing response times.
    
    This fixture helps measure and assert performance characteristics
    of API endpoints during testing.
    
    Yields:
        function: Timer function that returns elapsed time
    """
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            """Start the timer."""
            self.start_time = time.perf_counter()
        
        def stop(self):
            """Stop the timer and return elapsed time."""
            self.end_time = time.perf_counter()
            return self.end_time - self.start_time if self.start_time else 0
    
    yield Timer()


# =============================================================================
# Environment Configuration for Tests
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment configuration.
    
    This fixture runs automatically for all tests and ensures
    that the test environment is properly configured with
    appropriate settings and environment variables.
    """
    # Set test environment variables
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["USE_SQLITE_FALLBACK"] = "True"
    os.environ["DEBUG"] = "True"
    os.environ["DB_ECHO"] = "False"  # Disable SQL logging during tests
    
    # Ensure we're using test settings
    settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    settings.USE_SQLITE_FALLBACK = True
    settings.DEBUG = True
    settings.DB_ECHO = False
    
    yield
    
    # Cleanup environment variables if needed
    # (Usually not necessary as test processes are isolated)