"""
Tests for OCR Agent API endpoints.

This module contains comprehensive tests for the OCR agent functionality,
including document upload, processing, status checking, and error handling.
"""

import json
import uuid
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import UploadFile
from httpx import AsyncClient
from PIL import Image

from src.models.claim import Claim, ClaimStatus


class TestOCRAgentAPI:
    """Test suite for OCR Agent API endpoints."""

    @pytest_asyncio.fixture
    async def ocr_ready_claim(self, test_db_session, sample_claim_data):
        """Create a claim with status suitable for OCR processing."""
        # Override status to ensure it's eligible for OCR processing
        claim_data = sample_claim_data.copy()
        claim_data["status"] = ClaimStatus.RECEIVED.value
        
        claim = Claim(**claim_data)
        test_db_session.add(claim)
        await test_db_session.commit()
        await test_db_session.refresh(claim)
        return claim

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_document_success(
        self,
        async_client: AsyncClient,
        ocr_ready_claim: Claim,
        mock_gcs_client: MagicMock,
    ):
        """
        Test successful document processing with OCR agent.
        
        This test verifies the complete OCR processing pipeline:
        - Document upload validation
        - GCS upload
        - OCR text extraction
        - Data structuring
        - Database updates
        """
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4 mock pdf content"
        files = {
            "file": ("test_claim.pdf", BytesIO(pdf_content), "application/pdf")
        }
        
        # Mock OCR agent processing
        with patch("src.agents.ocr_agent.ocr_agent.process_document") as mock_process:
            mock_process.return_value = {
                "gcs_uri": "gs://claims-documents/claims/test-claim/test_claim.pdf",
                "extracted_text": "Patient: John Doe\nAmount: $1500.00\nPolicy: POL123456",
                "structured_data": {
                    "patient_name": "John Doe",
                    "claim_amount": 1500.00,
                    "policy_number": "POL123456"
                },
                "confidence_scores": {
                    "patient_name": 0.95,
                    "claim_amount": 0.90,
                    "policy_number": 0.85
                },
                "overall_confidence": 0.90,
                "requires_human_review": False,
                "ocr_metadata": {
                    "extraction_method": "document_ai",
                    "page_count": 1,
                    "processing_time_seconds": 2.5
                }
            }
            
            # Make request
            response = await async_client.post(
                f"/api/v1/agents/ocr/process/{ocr_ready_claim.id}",
                files=files
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            
            assert data["processing_status"] == "completed"
            assert data["claim_status"] == "DQ_VALIDATED"
            assert data["confidence_score"] == 0.90
            assert not data["requires_human_review"]
            assert "John Doe" in data["extracted_data"]["patient_name"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_document_low_confidence(
        self,
        async_client: AsyncClient,
        ocr_ready_claim: Claim,
    ):
        """Test document processing with low confidence requiring human review."""
        # Create a mock image file
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {
            "file": ("test_image.png", img_bytes, "image/png")
        }
        
        # Mock OCR agent with low confidence
        with patch("src.agents.ocr_agent.ocr_agent.process_document") as mock_process:
            mock_process.return_value = {
                "gcs_uri": "gs://claims-documents/claims/test-claim/test_image.png",
                "extracted_text": "unclear text...",
                "structured_data": {
                    "patient_name": None,
                    "claim_amount": None,
                    "policy_number": None
                },
                "confidence_scores": {
                    "patient_name": 0.20,
                    "claim_amount": 0.30,
                    "policy_number": 0.15
                },
                "overall_confidence": 0.22,
                "requires_human_review": True,
                "ocr_metadata": {
                    "extraction_method": "vision_api",
                    "page_count": 1,
                    "processing_time_seconds": 1.8
                }
            }
            
            # Make request
            response = await async_client.post(
                f"/api/v1/agents/ocr/process/{ocr_ready_claim.id}",
                files=files
            )
            
            # Assert response
            assert response.status_code == 200
            data = response.json()
            
            assert data["processing_status"] == "completed"
            assert data["claim_status"] == "HUMAN_REVIEW"
            assert data["confidence_score"] == 0.22
            assert data["requires_human_review"] is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_document_invalid_claim(
        self,
        async_client: AsyncClient,
    ):
        """Test document processing with non-existent claim ID."""
        files = {
            "file": ("test.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")
        }
        
        fake_claim_id = uuid.uuid4()
        response = await async_client.post(
            f"/api/v1/agents/ocr/process/{fake_claim_id}",
            files=files
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_document_invalid_file_format(
        self,
        async_client: AsyncClient,
        ocr_ready_claim: Claim,
    ):
        """Test document processing with unsupported file format."""
        files = {
            "file": ("test.txt", BytesIO(b"text content"), "text/plain")
        }
        
        response = await async_client.post(
            f"/api/v1/agents/ocr/process/{ocr_ready_claim.id}",
            files=files
        )
        
        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_ocr_status_success(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test retrieving OCR processing status for a claim."""
        # Update claim with OCR data
        sample_claim_in_db.ocr_processed_at = datetime.utcnow()
        sample_claim_in_db.ocr_confidence_score = 0.85
        sample_claim_in_db.requires_human_review = False
        sample_claim_in_db.raw_data = {
            "structured_data": {"patient_name": "John Doe"},
            "ocr_metadata": {"processing_time": 2.5}
        }
        
        response = await async_client.get(
            f"/api/v1/agents/ocr/status/{sample_claim_in_db.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["claim_id"] == str(sample_claim_in_db.id)
        assert data["ocr_processed"] is True
        assert data["confidence_score"] == 0.85
        assert data["requires_human_review"] is False
        assert "John Doe" in data["extracted_data"]["patient_name"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_ocr_status_not_processed(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test retrieving OCR status for claim that hasn't been processed."""
        response = await async_client.get(
            f"/api/v1/agents/ocr/status/{sample_claim_in_db.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["claim_id"] == str(sample_claim_in_db.id)
        assert data["ocr_processed"] is False
        assert data["ocr_processed_at"] is None
        assert data["confidence_score"] is None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_claim_documents(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test listing documents associated with a claim."""
        with patch("src.utils.gcs_helper.gcs_manager.list_claim_documents") as mock_list:
            mock_list.return_value = [
                {
                    "name": f"claims/{sample_claim_in_db.id}/doc1.pdf",
                    "filename": "doc1.pdf",
                    "size": 1024,
                    "content_type": "application/pdf",
                    "created": "2024-01-01T00:00:00Z",
                    "gcs_uri": f"gs://claims-documents/claims/{sample_claim_in_db.id}/doc1.pdf"
                }
            ]
            
            response = await async_client.get(
                f"/api/v1/agents/ocr/documents/{sample_claim_in_db.id}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["claim_id"] == str(sample_claim_in_db.id)
            assert data["document_count"] == 1
            assert len(data["documents"]) == 1
            assert data["documents"][0]["filename"] == "doc1.pdf"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_claim_document(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test deleting a specific document from a claim."""
        with patch("src.utils.gcs_helper.gcs_manager.delete_blob") as mock_delete:
            mock_delete.return_value = True
            
            response = await async_client.delete(
                f"/api/v1/agents/ocr/documents/{sample_claim_in_db.id}/test_doc.pdf"
            )
            
            assert response.status_code == 204
            mock_delete.assert_called_once_with(f"claims/{sample_claim_in_db.id}/test_doc.pdf")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reprocess_claim_success(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test reprocessing a claim with existing documents."""
        # Set up claim with existing document
        sample_claim_in_db.document_url = "gs://claims-documents/claims/test/doc.pdf"
        
        with patch("src.utils.gcs_helper.gcs_manager.get_blob_content") as mock_content, \
             patch("src.utils.gcs_helper.gcs_manager.get_blob_metadata") as mock_metadata, \
             patch("src.agents.ocr_agent.ocr_agent.process_document") as mock_process:
            
            # Mock GCS operations
            mock_content.return_value = b"%PDF-1.4 content"
            mock_metadata.return_value = {
                "content_type": "application/pdf",
                "size": 1024
            }
            
            # Mock OCR processing
            mock_process.return_value = {
                "gcs_uri": "gs://claims-documents/claims/test/doc.pdf",
                "extracted_text": "Reprocessed text",
                "structured_data": {"patient_name": "Jane Doe"},
                "confidence_scores": {"patient_name": 0.95},
                "overall_confidence": 0.95,
                "requires_human_review": False,
                "ocr_metadata": {"method": "reprocessing"}
            }
            
            response = await async_client.post(
                f"/api/v1/agents/ocr/reprocess/{sample_claim_in_db.id}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["reprocessing_status"] == "completed"
            assert data["new_confidence_score"] == 0.95
            assert not data["requires_human_review"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_ocr_agent_processing_error(
        self,
        async_client: AsyncClient,
        sample_claim_in_db: Claim,
    ):
        """Test handling of OCR processing errors."""
        files = {
            "file": ("test.pdf", BytesIO(b"%PDF-1.4"), "application/pdf")
        }
        
        with patch("src.agents.ocr_agent.ocr_agent.process_document") as mock_process:
            mock_process.side_effect = Exception("OCR service unavailable")
            
            response = await async_client.post(
                f"/api/v1/agents/ocr/process/{sample_claim_in_db.id}",
                files=files
            )
            
            assert response.status_code == 500
            assert "OCR processing failed" in response.json()["detail"]


class TestOCRAgentUnit:
    """Unit tests for OCR Agent components."""

    @pytest.mark.unit
    def test_validate_file_format_valid(self):
        """Test file format validation with valid formats."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # Test valid PDF
        mock_file = MagicMock()
        mock_file.content_type = "application/pdf"
        mock_file.filename = "test.pdf"
        
        assert agent._validate_file_format(mock_file) is True

    @pytest.mark.unit  
    def test_validate_file_format_invalid(self):
        """Test file format validation with invalid formats."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        from fastapi import HTTPException
        
        agent = ADKIngestOCRAgent()
        
        # Test invalid format
        mock_file = MagicMock()
        mock_file.content_type = "text/plain"
        mock_file.filename = "test.txt"
        
        with pytest.raises(HTTPException) as exc_info:
            agent._validate_file_format(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "Unsupported file format" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_extract_patient_name(self):
        """Test patient name extraction from text."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # Test various text patterns
        test_cases = [
            ("Patient: John Doe", "John Doe"),
            ("Name: Jane Smith", "Jane Smith"),
            ("Insured: Bob Wilson", "Bob Wilson"),
            ("Random text without name", None)
        ]
        
        for text, expected in test_cases:
            result = agent._extract_patient_name(text)
            assert result == expected

    @pytest.mark.unit
    def test_extract_claim_amount(self):
        """Test claim amount extraction from text."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # Test various amount patterns
        test_cases = [
            ("Amount: $1,500.00", 1500.00),
            ("Total: 2500", 2500.00),
            ("Charge: $750.50", 750.50),
            ("No amount here", None)
        ]
        
        for text, expected in test_cases:
            result = agent._extract_claim_amount(text)
            assert result == expected

    @pytest.mark.unit
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        ocr_confidence = 0.8
        structured_confidence = {
            "patient_name": 0.9,
            "claim_amount": 0.7,
            "policy_number": 0.8
        }
        
        # OCR confidence (40%) + structured average (60%)
        expected = (0.8 * 0.4) + (0.8 * 0.6)  # 0.8
        result = agent._calculate_overall_confidence(ocr_confidence, structured_confidence)
        
        assert abs(result - expected) < 0.01

    @pytest.mark.unit
    def test_requires_human_review_low_confidence(self):
        """Test human review requirement for low confidence."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # Low confidence should require review
        result = agent._requires_human_review(0.5, {"patient_name": "John Doe"})
        assert result is True

    @pytest.mark.unit
    def test_requires_human_review_missing_critical_fields(self):
        """Test human review requirement for missing critical fields."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # Missing patient name should require review
        result = agent._requires_human_review(0.9, {"claim_amount": 1500.0})
        assert result is True
        
        # Missing claim amount should require review
        result = agent._requires_human_review(0.9, {"patient_name": "John Doe"})
        assert result is True

    @pytest.mark.unit
    def test_requires_human_review_good_data(self):
        """Test human review not required for good data."""
        from src.agents.ocr_agent import ADKIngestOCRAgent
        
        agent = ADKIngestOCRAgent()
        
        # High confidence with all critical fields should not require review
        result = agent._requires_human_review(
            0.9, 
            {"patient_name": "John Doe", "claim_amount": 1500.0}
        )
        assert result is False


class TestGCSHelper:
    """Tests for GCS helper utilities."""

    @pytest.mark.unit
    def test_generate_signed_url(self):
        """Test signed URL generation."""
        from src.utils.gcs_helper import GCSManager
        
        with patch("src.utils.gcs_helper.storage.Client") as mock_client_class:
            # Mock GCS client and bucket
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            
            mock_client_class.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"
            
            # Test signed URL generation
            gcs_manager = GCSManager()
            gcs_manager.client = mock_client
            
            result = gcs_manager.generate_signed_url("test/blob")
            
            assert result == "https://signed-url.example.com"
            mock_blob.generate_signed_url.assert_called_once()

    @pytest.mark.unit
    def test_list_claim_documents(self):
        """Test listing claim documents."""
        from src.utils.gcs_helper import GCSManager
        
        with patch("src.utils.gcs_helper.storage.Client") as mock_client_class:
            # Mock GCS client and bucket
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            
            mock_client_class.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            
            # Mock blob properties
            mock_blob.name = "claims/test-id/doc.pdf"
            mock_blob.size = 1024
            mock_blob.content_type = "application/pdf"
            mock_blob.time_created = datetime(2024, 1, 1)
            mock_blob.metadata = {"custom": "data"}
            
            mock_bucket.list_blobs.return_value = [mock_blob]
            
            # Test document listing
            gcs_manager = GCSManager()
            gcs_manager.client = mock_client
            
            result = gcs_manager.list_claim_documents(uuid.uuid4())
            
            assert len(result) == 1
            assert result[0]["filename"] == "doc.pdf"
            assert result[0]["size"] == 1024
            assert result[0]["content_type"] == "application/pdf"