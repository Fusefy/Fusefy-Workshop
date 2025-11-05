"""
Configuration for OCR Agent testing.

This module provides environment setup and configuration
for comprehensive OCR agent testing.
"""

import os
from pathlib import Path

import pytest


# Test environment configuration
TEST_CONFIG = {
    # Database configuration
    "database_url": os.getenv("TEST_DATABASE_URL", "sqlite:///./test_claims.db"),
    
    # Google Cloud configuration (mocked in tests)
    "gcp_project_id": "test-project",
    "gcs_bucket_name": "test-claims-documents", 
    "document_ai_processor_id": "test-processor-123",
    "document_ai_location": "us",
    
    # OCR processing configuration
    "confidence_threshold": 0.7,
    "human_review_threshold": 0.6,
    "max_file_size_mb": 50,
    "processing_timeout_seconds": 300,
    
    # Supported file formats for OCR
    "supported_formats": [
        "application/pdf",
        "image/png",
        "image/jpeg", 
        "image/jpg",
        "image/tiff",
        "image/tif"
    ],
    
    # Test data paths
    "test_data_dir": Path(__file__).parent / "data",
    "sample_documents_dir": Path(__file__).parent / "data" / "sample_documents"
}


# Test markers configuration
def pytest_configure(config):
    """Configure pytest markers for OCR testing."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for OCR components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for OCR API endpoints" 
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end OCR processing tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests (actual cloud services)"
    )
    config.addinivalue_line(
        "markers", "gcp: Tests requiring Google Cloud Platform services"
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection for OCR testing."""
    # Add markers automatically based on test names
    for item in items:
        # Mark unit tests
        if "unit" in item.nodeid.lower():
            item.add_marker(pytest.mark.unit)
        
        # Mark integration tests
        if "integration" in item.nodeid.lower() or "test_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark end-to-end tests
        if "e2e" in item.nodeid.lower() or "end_to_end" in item.nodeid.lower():
            item.add_marker(pytest.mark.e2e)
        
        # Mark GCP tests
        if any(keyword in item.nodeid.lower() for keyword in ["gcs", "document_ai", "vision"]):
            item.add_marker(pytest.mark.gcp)


# Environment setup for testing
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment for OCR testing."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["GCP_PROJECT_ID"] = TEST_CONFIG["gcp_project_id"]
    os.environ["GCS_BUCKET_NAME"] = TEST_CONFIG["gcs_bucket_name"]
    os.environ["DOCUMENT_AI_PROCESSOR_ID"] = TEST_CONFIG["document_ai_processor_id"]
    
    # Disable actual GCP authentication in tests
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    
    # Create test data directories
    TEST_CONFIG["test_data_dir"].mkdir(exist_ok=True)
    TEST_CONFIG["sample_documents_dir"].mkdir(exist_ok=True)
    
    yield
    
    # Cleanup test environment
    test_vars = ["TESTING", "GCP_PROJECT_ID", "GCS_BUCKET_NAME", "DOCUMENT_AI_PROCESSOR_ID"]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]


def skip_if_no_gcp_credentials():
    """Skip test if GCP credentials are not available."""
    return pytest.mark.skipif(
        not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("TESTING"),
        reason="GCP credentials not available or in testing mode"
    )


def skip_if_no_internet():
    """Skip test if internet connection is not available."""
    import socket
    
    def can_connect():
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    return pytest.mark.skipif(
        not can_connect(),
        reason="Internet connection required for this test"
    )


# Test data utilities
class TestDataGenerator:
    """Generate test data for OCR testing."""
    
    @staticmethod
    def create_sample_claim_text():
        """Create sample claim text for OCR extraction."""
        return """
        MEDICAL CLAIM FORM
        
        Patient Information:
        Name: John Doe
        Date of Birth: 01/15/1980
        Policy Number: POL123456789
        
        Service Information:
        Date of Service: 03/15/2024
        Provider: Test Medical Center
        Provider ID: PROV001
        
        Claim Details:
        Diagnosis Code: M54.5 - Low back pain
        Procedure Code: 99213 - Office visit
        Charge Amount: $1,500.00
        
        Additional Information:
        Prior Authorization: AUTH123
        Referring Physician: Dr. Smith
        """
    
    @staticmethod
    def create_poor_quality_text():
        """Create poor quality text that should trigger human review."""
        return """
        MEDI??L CL??? F?RM
        
        Pat??nt: J?hn D??
        Pol??y: POL???456
        Am??nt: $1,5??.??
        
        [Text unclear and partially illegible]
        """
    
    @staticmethod
    def create_structured_claim_data():
        """Create structured claim data for testing."""
        return {
            "patient_name": "John Doe",
            "date_of_birth": "01/15/1980", 
            "policy_number": "POL123456789",
            "date_of_service": "03/15/2024",
            "provider_name": "Test Medical Center",
            "provider_id": "PROV001",
            "diagnosis_codes": ["M54.5"],
            "procedure_codes": ["99213"],
            "claim_amount": 1500.00,
            "prior_authorization": "AUTH123"
        }


# Performance testing utilities
class OCRPerformanceMetrics:
    """Track performance metrics for OCR testing."""
    
    def __init__(self):
        self.metrics = {
            "processing_times": [],
            "confidence_scores": [],
            "file_sizes": [],
            "success_rates": []
        }
    
    def record_processing_time(self, time_seconds: float):
        """Record OCR processing time."""
        self.metrics["processing_times"].append(time_seconds)
    
    def record_confidence_score(self, score: float):
        """Record OCR confidence score."""
        self.metrics["confidence_scores"].append(score)
    
    def record_file_size(self, size_bytes: int):
        """Record processed file size."""
        self.metrics["file_sizes"].append(size_bytes)
    
    def get_summary(self):
        """Get performance metrics summary."""
        if not self.metrics["processing_times"]:
            return {"status": "no_data"}
        
        import statistics
        
        return {
            "avg_processing_time": statistics.mean(self.metrics["processing_times"]),
            "max_processing_time": max(self.metrics["processing_times"]),
            "min_processing_time": min(self.metrics["processing_times"]),
            "avg_confidence": statistics.mean(self.metrics["confidence_scores"]) if self.metrics["confidence_scores"] else 0,
            "total_files_processed": len(self.metrics["processing_times"])
        }