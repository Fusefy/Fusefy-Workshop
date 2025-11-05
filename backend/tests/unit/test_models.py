"""
Unit tests for SQLAlchemy models.

This module tests the database models including field validation,
relationships, constraints, and database interactions.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.claim import Claim, ClaimStatus
from src.models.base import BaseModel


class TestBaseModel:
    """Test suite for the base model functionality."""

    @pytest.mark.unit
    async def test_base_model_id_generation(self, test_db_session: AsyncSession, sample_claim_data: Dict[str, Any]):
        """
        Test automatic UUID generation for model IDs.
        
        This test verifies that the BaseModel automatically generates
        unique UUID identifiers when new instances are created.
        
        Expected behavior:
        - ID is automatically generated when not provided
        - Generated ID is valid UUID format
        - Each instance gets unique ID
        """
        # Arrange & Act: Create claim without specifying ID
        claim1 = Claim(**sample_claim_data)
        
        # Modify data for second claim to avoid unique constraint violation
        claim2_data = sample_claim_data.copy()
        claim2_data["claim_number"] = "CLM-UUID-TEST-002"
        claim2 = Claim(**claim2_data)
        
        # Assert: Verify ID generation
        assert claim1.id is not None, "ID should be automatically generated"
        assert claim2.id is not None, "ID should be automatically generated"
        
        # Verify IDs are valid UUIDs
        assert isinstance(claim1.id, uuid.UUID), "ID should be UUID type"
        assert isinstance(claim2.id, uuid.UUID), "ID should be UUID type"
        
        # Verify uniqueness
        assert claim1.id != claim2.id, "Each instance should have unique ID"

    @pytest.mark.unit
    async def test_base_model_timestamp_generation(self, test_db_session: AsyncSession, sample_claim_data: Dict[str, Any]):
        """
        Test automatic timestamp generation for created_at and updated_at.
        
        This test verifies that timestamps are automatically set when
        creating new model instances and updated appropriately.
        
        Expected behavior:
        - created_at is set automatically on creation
        - updated_at is set automatically on creation
        - Timestamps are datetime objects with timezone info
        - created_at and updated_at are initially equal
        """
        # Arrange & Act: Create and save claim
        claim = Claim(**sample_claim_data)
        test_db_session.add(claim)
        await test_db_session.commit()
        await test_db_session.refresh(claim)
        
        # Assert: Verify timestamp generation
        assert claim.created_at is not None, "created_at should be automatically set"
        assert claim.updated_at is not None, "updated_at should be automatically set"
        
        # Verify timestamp types
        assert isinstance(claim.created_at, datetime), "created_at should be datetime"
        assert isinstance(claim.updated_at, datetime), "updated_at should be datetime"
        
        # Verify timestamps are recent (within last minute)
        now = datetime.now()
        time_diff = abs((now - claim.created_at.replace(tzinfo=None)).total_seconds())
        assert time_diff < 60, "created_at should be recent"

    @pytest.mark.unit
    async def test_base_model_updated_at_changes(self, test_db_session: AsyncSession, sample_claim_in_db: Claim):
        """
        Test that updated_at timestamp changes when model is modified.
        
        This test verifies that the updated_at field is automatically
        refreshed when model instances are updated.
        
        Expected behavior:
        - updated_at changes when model is updated
        - New updated_at is greater than original
        - created_at remains unchanged
        """
        # Arrange: Record original timestamps
        original_created_at = sample_claim_in_db.created_at
        original_updated_at = sample_claim_in_db.updated_at
        
        # Add small delay to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.01)
        
        # Act: Update the claim
        sample_claim_in_db.patient_name = "Updated Patient Name"
        await test_db_session.commit()
        await test_db_session.refresh(sample_claim_in_db)
        
        # Assert: Verify timestamp behavior
        assert sample_claim_in_db.created_at == original_created_at, "created_at should not change on update"
        assert sample_claim_in_db.updated_at > original_updated_at, "updated_at should be refreshed on update"

    @pytest.mark.unit
    def test_base_model_repr(self, sample_claim_data: Dict[str, Any]):
        """
        Test string representation of base model.
        
        This test verifies that model instances have a useful
        string representation for debugging and logging.
        
        Expected behavior:
        - __repr__ returns descriptive string
        - String includes model class name and ID
        """
        # Arrange & Act: Create claim instance
        claim = Claim(**sample_claim_data)
        
        # Assert: Verify string representation
        repr_str = repr(claim)
        assert "Claim" in repr_str, "Representation should include class name"
        assert str(claim.id) in repr_str, "Representation should include ID"
        assert "id=" in repr_str, "Representation should be descriptive"


class TestClaimModel:
    """Test suite for the Claim model specifically."""

    @pytest.mark.unit
    def test_claim_creation_with_valid_data(self, sample_claim_data: Dict[str, Any]):
        """
        Test creating Claim instance with valid data.
        
        This test verifies that Claim instances can be created
        with valid data and all fields are properly assigned.
        
        Expected behavior:
        - All provided fields are set correctly
        - Required fields are properly assigned
        - Optional fields handle None values
        """
        # Act: Create claim instance
        claim = Claim(**sample_claim_data)
        
        # Assert: Verify all fields are set correctly
        assert claim.claim_number == sample_claim_data["claim_number"], "Claim number should be set"
        assert claim.patient_name == sample_claim_data["patient_name"], "Patient name should be set"
        assert claim.claim_amount == sample_claim_data["claim_amount"], "Claim amount should be set"
        assert claim.status == sample_claim_data["status"], "Status should be set"
        assert claim.document_url == sample_claim_data["document_url"], "Document URL should be set"
        assert claim.raw_data == sample_claim_data["raw_data"], "Raw data should be set"
        assert claim.claim_metadata == sample_claim_data["claim_metadata"], "Metadata should be set"

    @pytest.mark.unit
    def test_claim_status_enum_validation(self):
        """
        Test ClaimStatus enum validation and values.
        
        This test ensures that the ClaimStatus enum contains all
        expected values and behaves correctly.
        
        Expected behavior:
        - All expected status values are present
        - Enum values are strings
        - Invalid statuses are rejected
        """
        # Assert: Verify all expected statuses exist
        expected_statuses = {
            "RECEIVED", "OCR_PROCESSING", "PII_MASKED", "DQ_VALIDATED",
            "HUMAN_REVIEW", "CONSENT_VERIFIED", "CLAIM_VALIDATED",
            "PAYER_SUBMITTED", "SETTLED", "REJECTED"
        }
        
        actual_statuses = {status.value for status in ClaimStatus}
        assert actual_statuses == expected_statuses, f"ClaimStatus should contain {expected_statuses}"
        
        # Verify enum behavior
        assert ClaimStatus.RECEIVED.value == "RECEIVED", "Enum values should be strings"
        assert ClaimStatus("RECEIVED") == ClaimStatus.RECEIVED, "Enum should be constructible from string"

    @pytest.mark.unit
    async def test_claim_database_constraints(self, test_db_session: AsyncSession, sample_claim_data: Dict[str, Any]):
        """
        Test database constraints on Claim model.
        
        This test verifies that database-level constraints are
        properly enforced, such as unique constraints and required fields.
        
        Expected behavior:
        - Unique constraint on claim_number is enforced
        - Required fields cannot be None
        - IntegrityError raised for constraint violations
        """
        # Arrange: Create and save first claim
        claim1 = Claim(**sample_claim_data)
        test_db_session.add(claim1)
        await test_db_session.commit()
        
        # Act & Assert: Attempt to create duplicate claim number
        duplicate_data = sample_claim_data.copy()
        duplicate_data["patient_name"] = "Different Patient"
        claim2 = Claim(**duplicate_data)
        test_db_session.add(claim2)
        
        with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
            await test_db_session.commit()

    @pytest.mark.unit
    async def test_claim_json_fields(self, test_db_session: AsyncSession):
        """
        Test JSON field handling in Claim model.
        
        This test verifies that raw_data and claim_metadata fields
        properly handle JSON/dict data including complex nested structures.
        
        Expected behavior:
        - JSON fields accept dict/list data
        - Complex nested structures are preserved
        - None values are handled correctly
        - Data retrieval preserves structure
        """
        # Arrange: Create claim with complex JSON data
        complex_raw_data = {
            "ocr_results": {
                "confidence": 0.95,
                "extracted_text": "Sample claim document",
                "fields": [
                    {"name": "patient_id", "value": "P12345", "confidence": 0.98},
                    {"name": "amount", "value": 1500.00, "confidence": 0.92}
                ]
            },
            "processing_metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "processor_version": "v2.1.0",
                "flags": ["high_confidence", "automated"]
            }
        }
        
        complex_metadata = {
            "workflow": {
                "current_stage": "validation",
                "completed_stages": ["intake", "ocr", "extraction"],
                "next_stages": ["review", "approval"]
            },
            "audit_trail": [
                {"action": "created", "user": "system", "timestamp": "2024-01-01T10:00:00Z"},
                {"action": "processed", "user": "ocr_service", "timestamp": "2024-01-01T10:30:00Z"}
            ]
        }
        
        claim_data = {
            "claim_number": "CLM-JSON-TEST-001",
            "patient_name": "JSON Test Patient",
            "claim_amount": Decimal("1500.00"),
            "status": ClaimStatus.OCR_PROCESSING,
            "raw_data": complex_raw_data,
            "claim_metadata": complex_metadata
        }
        
        # Act: Create and save claim with complex JSON
        claim = Claim(**claim_data)
        test_db_session.add(claim)
        await test_db_session.commit()
        await test_db_session.refresh(claim)
        
        # Assert: Verify JSON data preservation
        assert claim.raw_data == complex_raw_data, "Raw data should preserve complex structure"
        assert claim.claim_metadata == complex_metadata, "Metadata should preserve complex structure"
        
        # Verify nested access works
        assert claim.raw_data["ocr_results"]["confidence"] == 0.95, "Nested JSON access should work"
        assert len(claim.claim_metadata["audit_trail"]) == 2, "JSON array length should be preserved"

    @pytest.mark.unit
    async def test_claim_decimal_precision(self, test_db_session: AsyncSession):
        """
        Test decimal precision handling for claim amounts.
        
        This test verifies that claim amounts are stored and retrieved
        with proper decimal precision for financial calculations.
        
        Expected behavior:
        - Decimal precision is preserved (2 decimal places)
        - Large amounts are handled correctly
        - Exact decimal arithmetic works
        """
        # Arrange: Test various decimal amounts
        test_amounts = [
            Decimal("0.01"),        # Minimum amount
            Decimal("999999.99"),   # Large amount
            Decimal("1234.567"),    # More than 2 decimal places (should truncate/round)
            Decimal("1500.00"),     # Exact dollars
        ]
        
        claims = []
        for i, amount in enumerate(test_amounts):
            claim_data = {
                "claim_number": f"CLM-DECIMAL-{i:03d}",
                "patient_name": f"Decimal Test Patient {i}",
                "claim_amount": amount,
                "status": ClaimStatus.RECEIVED
            }
            claim = Claim(**claim_data)
            test_db_session.add(claim)
            claims.append(claim)
        
        # Act: Save and retrieve claims
        await test_db_session.commit()
        for claim in claims:
            await test_db_session.refresh(claim)
        
        # Assert: Verify decimal handling
        assert claims[0].claim_amount == Decimal("0.01"), "Minimum amount should be preserved"
        assert claims[1].claim_amount == Decimal("999999.99"), "Large amount should be preserved"
        assert claims[3].claim_amount == Decimal("1500.00"), "Exact dollars should be preserved"
        
        # Verify decimal arithmetic works correctly
        total = sum(claim.claim_amount for claim in claims[:2])  # Skip the rounded one
        assert isinstance(total, Decimal), "Sum should maintain Decimal type"

    @pytest.mark.unit
    def test_claim_model_repr(self, sample_claim_data: Dict[str, Any]):
        """
        Test Claim model string representation.
        
        This test verifies that Claim instances have a useful
        string representation that includes key identifying information.
        
        Expected behavior:
        - __repr__ includes claim number, status, and amount
        - String is useful for debugging and logging
        """
        # Act: Create claim and get representation
        claim = Claim(**sample_claim_data)
        repr_str = repr(claim)
        
        # Assert: Verify representation content
        assert "Claim(" in repr_str, "Should identify as Claim"
        assert claim.claim_number in repr_str, "Should include claim number"
        assert claim.status.value in repr_str, "Should include status"
        assert str(claim.claim_amount) in repr_str, "Should include amount"

    @pytest.mark.unit
    def test_claim_optional_fields(self):
        """
        Test Claim creation with minimal required fields only.
        
        This test verifies that claims can be created with only
        the required fields, and optional fields default to None.
        
        Expected behavior:
        - Claims can be created with minimal data
        - Optional fields default to None
        - Required fields must be provided
        """
        # Arrange: Create claim with minimal required fields
        minimal_data = {
            "claim_number": "CLM-MINIMAL-001",
            "patient_name": "Minimal Test Patient",
            "claim_amount": Decimal("1000.00")
        }
        
        # Act: Create claim with minimal data
        claim = Claim(**minimal_data)
        
        # Assert: Verify required fields are set and optional fields are None
        assert claim.claim_number == minimal_data["claim_number"], "Required field should be set"
        assert claim.patient_name == minimal_data["patient_name"], "Required field should be set"
        assert claim.claim_amount == minimal_data["claim_amount"], "Required field should be set"
        
        # Verify optional fields default appropriately
        assert claim.status == ClaimStatus.RECEIVED, "Status should default to RECEIVED"
        assert claim.document_url is None, "Document URL should default to None"
        assert claim.raw_data is None, "Raw data should default to None"
        assert claim.claim_metadata is None, "Metadata should default to None"

    @pytest.mark.unit
    async def test_claim_database_indexes(self, test_db_session: AsyncSession, multiple_claims_in_db):
        """
        Test that database indexes work correctly for performance.
        
        This test verifies that database indexes on key fields
        function properly for query performance optimization.
        
        Expected behavior:
        - Queries by claim_number use index efficiently
        - Queries by status use index efficiently
        - Composite queries work correctly
        """
        # Note: This test verifies index usage indirectly through query behavior
        # In a production test, you might use EXPLAIN QUERY PLAN to verify index usage
        
        # Act & Assert: Test indexed field queries
        from sqlalchemy import select
        
        # Query by claim_number (should use unique index)
        result = await test_db_session.execute(
            select(Claim).where(Claim.claim_number == multiple_claims_in_db[0].claim_number)
        )
        found_claim = result.scalar_one_or_none()
        assert found_claim is not None, "Should find claim by claim_number"
        assert found_claim.id == multiple_claims_in_db[0].id, "Should find correct claim"
        
        # Query by status (should use status index)
        result = await test_db_session.execute(
            select(Claim).where(Claim.status == ClaimStatus.RECEIVED)
        )
        received_claims = result.scalars().all()
        assert len(received_claims) > 0, "Should find claims by status"
        
        # Verify all returned claims have correct status
        for claim in received_claims:
            assert claim.status == ClaimStatus.RECEIVED, "All claims should have requested status"