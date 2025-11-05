"""
Pytest fixtures for OCR agent testing.

This module provides shared fixtures for testing the OCR agent functionality,
including mock GCS clients, sample claims, and test data utilities.
"""

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.claim import Claim, ClaimStatus


@pytest.fixture
def sample_claim_data():
    """Provide sample claim data for testing."""
    return {
        "claim_number": f"CLM{uuid.uuid4().hex[:8].upper()}",
        "policy_number": "POL123456789",
        "patient_name": "John Doe",
        "claim_amount": Decimal("1500.00"),
        "status": ClaimStatus.RECEIVED.value,
        "provider_name": "Test Medical Center",
        "diagnosis_codes": ["Z00.00", "M54.5"],
        "procedure_codes": ["99213", "73060"],
        "raw_data": {
            "source": "test_system",
            "batch_id": "TEST_BATCH_001"
        }
    }


@pytest.fixture
async def sample_claim_in_db(db_session: Session, sample_claim_data: dict):
    """Create a sample claim in the test database."""
    claim = Claim(**sample_claim_data)
    db_session.add(claim)
    await db_session.commit()
    await db_session.refresh(claim)
    
    yield claim
    
    # Cleanup
    await db_session.delete(claim)
    await db_session.commit()


@pytest.fixture
def mock_gcs_client():
    """Mock Google Cloud Storage client for testing."""
    from unittest.mock import MagicMock, patch
    
    with patch("src.utils.gcs_helper.storage.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Configure mock client
        mock_client_class.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Configure mock blob operations
        mock_blob.upload_from_file.return_value = None
        mock_blob.generate_signed_url.return_value = "https://test-signed-url.com"
        mock_blob.download_as_bytes.return_value = b"mock file content"
        mock_blob.exists.return_value = True
        mock_blob.delete.return_value = None
        
        # Configure blob metadata
        mock_blob.name = "test-blob.pdf"
        mock_blob.size = 1024
        mock_blob.content_type = "application/pdf"
        mock_blob.time_created = datetime(2024, 1, 1)
        mock_blob.metadata = {}
        
        yield mock_client


@pytest.fixture
def mock_document_ai_client():
    """Mock Google Document AI client for testing."""
    from unittest.mock import MagicMock, patch
    
    with patch("src.agents.ocr_agent.documentai.DocumentProcessorServiceClient") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_document = MagicMock()
        
        # Configure mock client
        mock_client_class.return_value = mock_client
        mock_client.process_document.return_value = mock_response
        mock_response.document = mock_document
        
        # Configure mock document response
        mock_document.text = "Patient: John Doe\nAmount: $1,500.00\nPolicy: POL123456"
        
        # Mock pages and confidence
        mock_page = MagicMock()
        mock_page.page_number = 1
        mock_document.pages = [mock_page]
        
        yield mock_client


@pytest.fixture
def mock_vision_client():
    """Mock Google Vision API client for testing."""
    from unittest.mock import MagicMock, patch
    
    with patch("src.agents.ocr_agent.vision.ImageAnnotatorClient") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_annotation = MagicMock()
        
        # Configure mock client
        mock_client_class.return_value = mock_client
        mock_client.text_detection.return_value = mock_response
        
        # Configure mock response
        mock_annotation.description = "Patient: Jane Smith\nAmount: $2,000.00"
        mock_response.text_annotations = [mock_annotation]
        mock_response.error = None
        
        yield mock_client


@pytest.fixture
def mock_ocr_processing_result():
    """Provide a mock OCR processing result."""
    return {
        "gcs_uri": "gs://test-bucket/claims/test-id/document.pdf",
        "extracted_text": "Patient: John Doe\nDate of Service: 01/15/2024\nAmount: $1,500.00\nPolicy: POL123456789\nProvider: Test Medical Center",
        "structured_data": {
            "patient_name": "John Doe",
            "date_of_service": "01/15/2024", 
            "claim_amount": 1500.00,
            "policy_number": "POL123456789",
            "provider_name": "Test Medical Center"
        },
        "confidence_scores": {
            "patient_name": 0.95,
            "date_of_service": 0.90,
            "claim_amount": 0.88,
            "policy_number": 0.92,
            "provider_name": 0.87
        },
        "overall_confidence": 0.90,
        "requires_human_review": False,
        "ocr_metadata": {
            "extraction_method": "document_ai",
            "page_count": 1,
            "processing_time_seconds": 2.3,
            "document_type": "insurance_claim",
            "api_version": "v1"
        }
    }


@pytest.fixture
def mock_low_confidence_result():
    """Provide a mock OCR result with low confidence requiring human review."""
    return {
        "gcs_uri": "gs://test-bucket/claims/test-id/unclear_document.pdf",
        "extracted_text": "unclear text... partial recognition",
        "structured_data": {
            "patient_name": None,
            "date_of_service": None,
            "claim_amount": None,
            "policy_number": "POL???456", 
            "provider_name": None
        },
        "confidence_scores": {
            "patient_name": 0.20,
            "date_of_service": 0.15,
            "claim_amount": 0.10,
            "policy_number": 0.45,
            "provider_name": 0.25
        },
        "overall_confidence": 0.23,
        "requires_human_review": True,
        "ocr_metadata": {
            "extraction_method": "vision_api",
            "page_count": 1,
            "processing_time_seconds": 1.8,
            "document_type": "unknown",
            "quality_issues": ["low_resolution", "poor_contrast"]
        }
    }


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    from io import BytesIO
    
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Patient: John Doe) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000189 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
284
%%EOF"""
    
    return BytesIO(pdf_content)


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    from io import BytesIO
    from PIL import Image
    
    # Create a simple test image
    img = Image.new('RGB', (300, 200), color='white')
    
    # Add some text-like pattern (simple rectangles)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 250, 80], fill='black')  # Simulate text line
    draw.rectangle([50, 100, 200, 130], fill='black')  # Another text line
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes


@pytest.fixture
def ocr_agent_config():
    """Provide configuration for OCR agent testing."""
    return {
        "gcs_bucket_name": "test-claims-documents",
        "document_ai_processor_id": "test-processor-123",
        "document_ai_location": "us",
        "confidence_threshold": 0.7,
        "human_review_threshold": 0.6,
        "supported_formats": [
            "application/pdf",
            "image/png", 
            "image/jpeg",
            "image/tiff"
        ],
        "max_file_size_mb": 50,
        "processing_timeout_seconds": 300
    }


@pytest.fixture
async def claim_with_ocr_data(db_session: Session, sample_claim_data: dict):
    """Create a claim with existing OCR processing data."""
    ocr_data = {
        "structured_data": {
            "patient_name": "John Doe",
            "claim_amount": 1500.00,
            "policy_number": "POL123456789"
        },
        "ocr_metadata": {
            "extraction_method": "document_ai",
            "processing_time_seconds": 2.5,
            "page_count": 1
        }
    }
    
    claim_data = {
        **sample_claim_data,
        "document_url": "gs://test-bucket/claims/test/document.pdf",
        "ocr_processed_at": datetime.utcnow(),
        "ocr_confidence_score": 0.85,
        "requires_human_review": False,
        "raw_data": {**sample_claim_data.get("raw_data", {}), **ocr_data}
    }
    
    claim = Claim(**claim_data)
    db_session.add(claim)
    await db_session.commit()
    await db_session.refresh(claim)
    
    yield claim
    
    # Cleanup
    await db_session.delete(claim)
    await db_session.commit()


@pytest.fixture
def mock_litellm():
    """Mock LiteLLM for ADK agent testing."""
    from unittest.mock import MagicMock, patch
    
    with patch("src.agents.ocr_agent.litellm") as mock_litellm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = '{"confidence": 0.85, "structured": true}'
        
        mock_litellm.completion.return_value = mock_response
        
        yield mock_litellm