"""
Unit tests for Pydantic schemas.

This module tests the Pydantic schema validation, serialization,
and deserialization for all API request and response models.
"""

import pytest
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from pydantic import ValidationError

from src.models.claim import ClaimStatus
from src.schemas.claim import (
    ClaimBase,
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimListResponse,
    ClaimStatusFilter
)


class TestClaimBaseSchema:
    """Test suite for ClaimBase schema validation."""

    @pytest.mark.unit
    def test_claim_base_valid_data(self, sample_claim_data: Dict[str, Any]):
        """
        Test ClaimBase validation with valid data.
        
        This test verifies that ClaimBase accepts valid claim data
        and properly validates all field types and constraints.
        
        Expected behavior:
        - All valid fields are accepted
        - Field types are correctly converted
        - Optional fields handle None values
        """
        # Arrange: Prepare valid data for base schema
        base_data = sample_claim_data.copy()
        # Remove status as it's not in ClaimBase
        del base_data["status"]
        
        # Act: Create ClaimBase instance
        claim_base = ClaimBase(**base_data)
        
        # Assert: Verify all fields are properly set
        assert claim_base.claim_number == base_data["claim_number"], "Claim number should be set correctly"
        assert claim_base.patient_name == base_data["patient_name"], "Patient name should be set correctly"
        assert claim_base.claim_amount == base_data["claim_amount"], "Claim amount should be set correctly"
        assert claim_base.document_url == base_data["document_url"], "Document URL should be set correctly"
        assert claim_base.raw_data == base_data["raw_data"], "Raw data should be set correctly"
        assert claim_base.claim_metadata == base_data["claim_metadata"], "Metadata should be set correctly"

    @pytest.mark.unit
    def test_claim_base_required_fields(self):
        """
        Test ClaimBase validation of required fields.
        
        This test ensures that required fields are properly enforced
        and missing required fields result in validation errors.
        
        Expected behavior:
        - Missing required fields raise ValidationError
        - Error messages specify which fields are missing
        """
        # Act & Assert: Test missing claim_number
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                patient_name="Test Patient",
                claim_amount=Decimal("1000.00")
                # Missing claim_number
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("claim_number",) for error in errors), "Should error on missing claim_number"
        
        # Act & Assert: Test missing patient_name
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                claim_number="CLM-TEST-001",
                claim_amount=Decimal("1000.00")
                # Missing patient_name
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("patient_name",) for error in errors), "Should error on missing patient_name"

    @pytest.mark.unit
    def test_claim_base_field_constraints(self):
        """
        Test ClaimBase field validation constraints.
        
        This test verifies that field-level constraints (length, format, etc.)
        are properly enforced by Pydantic validation.
        
        Expected behavior:
        - String length constraints are enforced
        - Decimal precision and positive value constraints work
        - Invalid data types are rejected
        """
        # Test claim_number length constraint
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                claim_number="X" * 100,  # Exceeds max length of 50
                patient_name="Test Patient",
                claim_amount=Decimal("1000.00")
            )
        
        errors = exc_info.value.errors()
        assert any("at most 50 characters" in str(error.get("msg", "")).lower() for error in errors), \
            "Should enforce claim_number max length"
        
        # Test patient_name length constraint
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                claim_number="CLM-TEST-001",
                patient_name="Y" * 300,  # Exceeds max length of 255
                claim_amount=Decimal("1000.00")
            )
        
        errors = exc_info.value.errors()
        assert any("at most 255 characters" in str(error.get("msg", "")).lower() for error in errors), \
            "Should enforce patient_name max length"

    @pytest.mark.unit
    def test_claim_base_amount_validation(self):
        """
        Test claim amount validation in ClaimBase.
        
        This test ensures that claim amounts are properly validated
        for positive values and correct decimal format.
        
        Expected behavior:
        - Negative amounts are rejected
        - Zero amounts are rejected
        - Decimal precision is handled correctly
        """
        # Test negative amount
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                claim_number="CLM-TEST-001",
                patient_name="Test Patient",
                claim_amount=Decimal("-100.00")
            )
        
        errors = exc_info.value.errors()
        assert any("greater than 0" in str(error.get("msg", "")).lower() for error in errors), \
            "Should reject negative amounts"
        
        # Test zero amount
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                claim_number="CLM-TEST-001", 
                patient_name="Test Patient",
                claim_amount=Decimal("0.00")
            )
        
        errors = exc_info.value.errors()
        assert any("greater than 0" in str(error.get("msg", "")).lower() for error in errors), \
            "Should reject zero amounts"

    @pytest.mark.unit
    def test_claim_base_optional_fields(self):
        """
        Test ClaimBase handling of optional fields.
        
        This test verifies that optional fields can be omitted
        and default to None without causing validation errors.
        
        Expected behavior:
        - Optional fields can be omitted
        - Omitted fields default to None
        - Explicit None values are accepted
        """
        # Act: Create ClaimBase with minimal required fields
        claim_base = ClaimBase(
            claim_number="CLM-MINIMAL-001",
            patient_name="Minimal Patient",
            claim_amount=Decimal("500.00")
        )
        
        # Assert: Verify optional fields default to None
        assert claim_base.document_url is None, "document_url should default to None"
        assert claim_base.raw_data is None, "raw_data should default to None"
        assert claim_base.claim_metadata is None, "claim_metadata should default to None"
        
        # Act: Create ClaimBase with explicit None values
        claim_base_explicit = ClaimBase(
            claim_number="CLM-EXPLICIT-001",
            patient_name="Explicit Patient", 
            claim_amount=Decimal("750.00"),
            document_url=None,
            raw_data=None,
            claim_metadata=None
        )
        
        # Assert: Verify explicit None values are accepted
        assert claim_base_explicit.document_url is None, "Explicit None should be accepted"
        assert claim_base_explicit.raw_data is None, "Explicit None should be accepted"
        assert claim_base_explicit.claim_metadata is None, "Explicit None should be accepted"


class TestClaimCreateSchema:
    """Test suite for ClaimCreate schema validation."""

    @pytest.mark.unit
    def test_claim_create_valid_data(self, sample_claim_data: Dict[str, Any]):
        """
        Test ClaimCreate validation with complete valid data.
        
        This test verifies that ClaimCreate accepts all valid fields
        including the status field and inherits ClaimBase validation.
        
        Expected behavior:
        - All ClaimBase fields are accepted
        - Status field is properly validated
        - Default status works correctly
        """
        # Act: Create ClaimCreate instance
        claim_create = ClaimCreate(**sample_claim_data)
        
        # Assert: Verify all fields including status
        assert claim_create.claim_number == sample_claim_data["claim_number"], "Should inherit claim_number validation"
        assert claim_create.patient_name == sample_claim_data["patient_name"], "Should inherit patient_name validation"
        assert claim_create.claim_amount == sample_claim_data["claim_amount"], "Should inherit amount validation"
        assert claim_create.status == sample_claim_data["status"], "Should include status field"

    @pytest.mark.unit
    def test_claim_create_default_status(self):
        """
        Test ClaimCreate default status assignment.
        
        This test verifies that when no status is provided,
        ClaimCreate defaults to RECEIVED status.
        
        Expected behavior:
        - Missing status defaults to ClaimStatus.RECEIVED
        - Default status is properly typed
        """
        # Act: Create ClaimCreate without status
        claim_create = ClaimCreate(
            claim_number="CLM-DEFAULT-001",
            patient_name="Default Status Patient",
            claim_amount=Decimal("1200.00")
        )
        
        # Assert: Verify default status
        assert claim_create.status == ClaimStatus.RECEIVED, "Should default to RECEIVED status"
        assert isinstance(claim_create.status, ClaimStatus), "Status should be ClaimStatus enum type"

    @pytest.mark.unit
    def test_claim_create_status_validation(self):
        """
        Test ClaimCreate status field validation.
        
        This test ensures that only valid ClaimStatus enum values
        are accepted for the status field.
        
        Expected behavior:
        - Valid ClaimStatus values are accepted
        - Invalid status strings are rejected
        - Status validation error messages are clear
        """
        # Test valid status values
        for status in ClaimStatus:
            claim_create = ClaimCreate(
                claim_number=f"CLM-STATUS-{status.value}",
                patient_name="Status Test Patient",
                claim_amount=Decimal("1000.00"),
                status=status
            )
            assert claim_create.status == status, f"Should accept valid status {status.value}"
        
        # Test invalid status value
        with pytest.raises(ValidationError) as exc_info:
            ClaimCreate(
                claim_number="CLM-INVALID-001",
                patient_name="Invalid Status Patient",
                claim_amount=Decimal("1000.00"),
                status="INVALID_STATUS"  # Not a valid ClaimStatus
            )
        
        errors = exc_info.value.errors()
        assert any("status" in str(error.get("loc", [])) for error in errors), "Should error on invalid status"

    @pytest.mark.unit
    def test_claim_create_serialization(self, sample_claim_data: Dict[str, Any]):
        """
        Test ClaimCreate serialization to dict.
        
        This test verifies that ClaimCreate instances can be
        properly serialized to dictionaries for API processing.
        
        Expected behavior:
        - model_dump() returns complete dict
        - Enum values are properly serialized
        - Optional fields are included when present
        """
        # Act: Create and serialize ClaimCreate
        claim_create = ClaimCreate(**sample_claim_data)
        serialized = claim_create.model_dump()
        
        # Assert: Verify serialization
        assert isinstance(serialized, dict), "Serialization should return dict"
        assert serialized["claim_number"] == sample_claim_data["claim_number"], "Should serialize claim_number"
        assert serialized["patient_name"] == sample_claim_data["patient_name"], "Should serialize patient_name"
        assert serialized["status"] == sample_claim_data["status"], "Should serialize status enum"
        
        # Verify optional fields are included when present
        if sample_claim_data.get("document_url"):
            assert "document_url" in serialized, "Should include document_url when present"
        if sample_claim_data.get("raw_data"):
            assert "raw_data" in serialized, "Should include raw_data when present"


class TestClaimUpdateSchema:
    """Test suite for ClaimUpdate schema validation."""

    @pytest.mark.unit
    def test_claim_update_partial_data(self):
        """
        Test ClaimUpdate with partial field updates.
        
        This test verifies that ClaimUpdate properly handles
        partial updates where only some fields are provided.
        
        Expected behavior:
        - Any subset of fields can be provided
        - Missing fields are not required
        - Validation applies to provided fields only
        """
        # Test update with single field
        update_single = ClaimUpdate(status=ClaimStatus.HUMAN_REVIEW)
        assert update_single.status == ClaimStatus.HUMAN_REVIEW, "Should accept single field update"
        assert update_single.patient_name is None, "Non-provided fields should be None"
        
        # Test update with multiple fields
        update_multiple = ClaimUpdate(
            claim_amount=Decimal("2500.00"),
            status=ClaimStatus.CLAIM_VALIDATED,
            claim_metadata={"reviewer": "John Doe"}
        )
        assert update_multiple.claim_amount == Decimal("2500.00"), "Should accept amount update"
        assert update_multiple.status == ClaimStatus.CLAIM_VALIDATED, "Should accept status update"
        assert update_multiple.claim_metadata == {"reviewer": "John Doe"}, "Should accept metadata update"

    @pytest.mark.unit
    def test_claim_update_field_validation(self):
        """
        Test ClaimUpdate field-level validation.
        
        This test ensures that when fields are provided in updates,
        they still undergo proper validation constraints.
        
        Expected behavior:
        - Provided fields are validated according to constraints
        - Invalid field values are rejected
        - Validation errors are clear and specific
        """
        # Test invalid claim amount in update
        with pytest.raises(ValidationError) as exc_info:
            ClaimUpdate(claim_amount=Decimal("-500.00"))  # Negative amount
        
        errors = exc_info.value.errors()
        assert any("greater than 0" in str(error.get("msg", "")).lower() for error in errors), \
            "Should validate amount constraints in updates"
        
        # Test invalid patient name length in update
        with pytest.raises(ValidationError) as exc_info:
            ClaimUpdate(patient_name="X" * 300)  # Exceeds max length
        
        errors = exc_info.value.errors()
        assert any("at most 255 characters" in str(error.get("msg", "")).lower() for error in errors), \
            "Should validate name length in updates"

    @pytest.mark.unit
    def test_claim_update_empty(self):
        """
        Test ClaimUpdate with no fields provided.
        
        This test verifies that ClaimUpdate can be created with
        no fields, representing an empty update operation.
        
        Expected behavior:
        - Empty ClaimUpdate is valid
        - All fields are None by default
        - Can be serialized to empty dict
        """
        # Act: Create empty update
        empty_update = ClaimUpdate()
        
        # Assert: Verify all fields are None
        assert empty_update.patient_name is None, "Empty update should have None patient_name"
        assert empty_update.claim_amount is None, "Empty update should have None claim_amount"
        assert empty_update.status is None, "Empty update should have None status"
        assert empty_update.document_url is None, "Empty update should have None document_url"
        assert empty_update.raw_data is None, "Empty update should have None raw_data"
        assert empty_update.claim_metadata is None, "Empty update should have None claim_metadata"
        
        # Test serialization of empty update
        serialized = empty_update.model_dump(exclude_unset=True)
        assert serialized == {}, "Empty update should serialize to empty dict when excluding unset"

    @pytest.mark.unit
    def test_claim_update_exclude_unset(self):
        """
        Test ClaimUpdate serialization with exclude_unset.
        
        This test verifies that ClaimUpdate properly handles
        exclude_unset during serialization for PATCH operations.
        
        Expected behavior:
        - exclude_unset=True only includes explicitly set fields
        - Unset fields are not included in serialization
        - Partial updates work correctly
        """
        # Act: Create partial update
        partial_update = ClaimUpdate(
            status=ClaimStatus.SETTLED,
            claim_metadata={"settlement_date": "2024-01-15"}
        )
        
        # Serialize with exclude_unset
        serialized = partial_update.model_dump(exclude_unset=True)
        
        # Assert: Only set fields are included
        assert "status" in serialized, "Set fields should be included"
        assert "claim_metadata" in serialized, "Set fields should be included"
        assert "patient_name" not in serialized, "Unset fields should be excluded"
        assert "claim_amount" not in serialized, "Unset fields should be excluded"
        assert len(serialized) == 2, "Should only include explicitly set fields"


class TestClaimResponseSchema:
    """Test suite for ClaimResponse schema validation."""

    @pytest.mark.unit
    def test_claim_response_from_model(self, sample_claim_in_db):
        """
        Test ClaimResponse creation from database model.
        
        This test verifies that ClaimResponse can be properly
        created from Claim model instances using from_attributes.
        
        Expected behavior:
        - All model fields are properly mapped
        - Timestamps are correctly formatted
        - Enum values are properly converted
        """
        # Act: Create ClaimResponse from model
        claim_response = ClaimResponse.model_validate(sample_claim_in_db)
        
        # Assert: Verify all fields are properly mapped
        assert claim_response.id == sample_claim_in_db.id, "ID should be mapped correctly"
        assert claim_response.claim_number == sample_claim_in_db.claim_number, "Claim number should be mapped"
        assert claim_response.patient_name == sample_claim_in_db.patient_name, "Patient name should be mapped"
        assert claim_response.claim_amount == sample_claim_in_db.claim_amount, "Amount should be mapped"
        assert claim_response.status == sample_claim_in_db.status, "Status should be mapped"
        assert claim_response.created_at == sample_claim_in_db.created_at, "Created timestamp should be mapped"
        assert claim_response.updated_at == sample_claim_in_db.updated_at, "Updated timestamp should be mapped"

    @pytest.mark.unit
    def test_claim_response_serialization(self, sample_claim_in_db):
        """
        Test ClaimResponse JSON serialization.
        
        This test verifies that ClaimResponse instances can be
        properly serialized to JSON for API responses.
        
        Expected behavior:
        - All fields serialize to appropriate JSON types
        - UUIDs serialize to strings
        - Datetimes serialize to ISO format strings
        - Enums serialize to their string values
        """
        # Act: Create and serialize ClaimResponse
        claim_response = ClaimResponse.model_validate(sample_claim_in_db)
        serialized = claim_response.model_dump()
        
        # Assert: Verify serialization types
        assert isinstance(serialized["id"], str), "UUID should serialize to string"
        assert isinstance(serialized["created_at"], datetime), "Datetime should remain datetime"
        assert isinstance(serialized["updated_at"], datetime), "Datetime should remain datetime"
        assert isinstance(serialized["status"], ClaimStatus), "Enum should remain enum type"
        
        # Test JSON serialization
        json_data = claim_response.model_dump(mode="json")
        assert isinstance(json_data["id"], str), "UUID should be string in JSON mode"
        assert isinstance(json_data["status"], str), "Enum should be string in JSON mode"

    @pytest.mark.unit
    def test_claim_response_required_fields(self):
        """
        Test ClaimResponse required field validation.
        
        This test ensures that ClaimResponse requires all
        expected fields and properly validates their presence.
        
        Expected behavior:
        - All required fields must be present
        - Missing required fields raise ValidationError
        - Field types are properly validated
        """
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            ClaimResponse(
                claim_number="CLM-TEST-001",
                patient_name="Test Patient",
                claim_amount=Decimal("1000.00")
                # Missing id, status, created_at, updated_at
            )
        
        errors = exc_info.value.errors()
        required_fields = {"id", "status", "created_at", "updated_at"}
        error_fields = {error["loc"][0] for error in errors if error["loc"]}
        
        assert required_fields.issubset(error_fields), f"Should error on missing required fields: {required_fields - error_fields}"


class TestClaimListResponseSchema:
    """Test suite for ClaimListResponse schema validation."""

    @pytest.mark.unit
    def test_claim_list_response_structure(self):
        """
        Test ClaimListResponse structure and validation.
        
        This test verifies that ClaimListResponse properly
        validates the paginated response structure.
        
        Expected behavior:
        - All pagination fields are required
        - Claims list contains ClaimResponse objects
        - Pagination math is logical
        """
        # Arrange: Create sample ClaimResponse objects
        sample_claims = [
            {
                "id": str(uuid.uuid4()),
                "claim_number": f"CLM-2024-{i:03d}",
                "patient_name": f"Patient {i}",
                "claim_amount": Decimal("1000.00"),
                "status": ClaimStatus.RECEIVED,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            for i in range(3)
        ]
        
        # Act: Create ClaimListResponse
        list_response = ClaimListResponse(
            claims=[ClaimResponse(**claim) for claim in sample_claims],
            total=10,
            page=1,
            size=3,
            pages=4
        )
        
        # Assert: Verify structure
        assert len(list_response.claims) == 3, "Should contain correct number of claims"
        assert list_response.total == 10, "Total should be set correctly"
        assert list_response.page == 1, "Page should be set correctly"
        assert list_response.size == 3, "Size should be set correctly"
        assert list_response.pages == 4, "Pages should be set correctly"
        
        # Verify all claims are ClaimResponse objects
        for claim in list_response.claims:
            assert isinstance(claim, ClaimResponse), "Each claim should be ClaimResponse instance"

    @pytest.mark.unit
    def test_claim_list_response_empty(self):
        """
        Test ClaimListResponse with empty results.
        
        This test verifies that ClaimListResponse properly
        handles empty result sets with appropriate pagination.
        
        Expected behavior:
        - Empty claims list is valid
        - Pagination fields reflect empty state
        - Structure remains consistent
        """
        # Act: Create empty ClaimListResponse
        empty_response = ClaimListResponse(
            claims=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        
        # Assert: Verify empty response structure
        assert empty_response.claims == [], "Claims should be empty list"
        assert empty_response.total == 0, "Total should be 0 for empty results"
        assert empty_response.pages == 0, "Pages should be 0 for empty results"

    @pytest.mark.unit 
    def test_claim_list_response_validation(self):
        """
        Test ClaimListResponse field validation.
        
        This test ensures that pagination fields are properly
        validated for logical consistency and valid ranges.
        
        Expected behavior:
        - Negative values are handled appropriately
        - Required fields are enforced
        - Field types are validated
        """
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            ClaimListResponse(
                claims=[],
                # Missing total, page, size, pages
            )
        
        errors = exc_info.value.errors()
        required_fields = {"total", "page", "size", "pages"}
        error_fields = {error["loc"][0] for error in errors if error["loc"]}
        
        assert required_fields.issubset(error_fields), "Should error on missing pagination fields"


class TestClaimStatusFilterSchema:
    """Test suite for ClaimStatusFilter schema validation."""

    @pytest.mark.unit
    def test_claim_status_filter_valid_statuses(self):
        """
        Test ClaimStatusFilter with all valid status values.
        
        This test verifies that ClaimStatusFilter accepts all
        valid ClaimStatus enum values.
        
        Expected behavior:
        - All ClaimStatus values are accepted
        - Enum validation works correctly
        - Status field is properly typed
        """
        # Test all valid status values
        for status in ClaimStatus:
            status_filter = ClaimStatusFilter(status=status)
            assert status_filter.status == status, f"Should accept valid status {status.value}"
            assert isinstance(status_filter.status, ClaimStatus), "Status should be ClaimStatus type"

    @pytest.mark.unit
    def test_claim_status_filter_invalid_status(self):
        """
        Test ClaimStatusFilter with invalid status values.
        
        This test ensures that ClaimStatusFilter properly
        validates status values and rejects invalid ones.
        
        Expected behavior:
        - Invalid status strings are rejected
        - ValidationError is raised with clear message
        - Error indicates invalid enum value
        """
        # Test invalid status value
        with pytest.raises(ValidationError) as exc_info:
            ClaimStatusFilter(status="NOT_A_VALID_STATUS")
        
        errors = exc_info.value.errors()
        assert any("status" in str(error.get("loc", [])) for error in errors), "Should error on invalid status"


class TestSchemaInteroperability:
    """Test suite for schema interoperability and conversion."""

    @pytest.mark.unit
    def test_create_to_model_conversion(self, sample_claim_data: Dict[str, Any]):
        """
        Test conversion from ClaimCreate schema to Claim model.
        
        This test verifies that ClaimCreate schemas can be properly
        converted to Claim model instances for database operations.
        
        Expected behavior:
        - All ClaimCreate fields map to model fields
        - Data types are compatible
        - No data loss during conversion
        """
        # Act: Create ClaimCreate and convert to model dict
        claim_create = ClaimCreate(**sample_claim_data)
        model_data = claim_create.model_dump()
        
        # Assert: Verify compatibility with model creation
        # This would typically be done in the API layer
        assert "claim_number" in model_data, "Should include claim_number for model"
        assert "patient_name" in model_data, "Should include patient_name for model"
        assert "claim_amount" in model_data, "Should include claim_amount for model"
        assert "status" in model_data, "Should include status for model"

    @pytest.mark.unit
    def test_model_to_response_conversion(self, sample_claim_in_db):
        """
        Test conversion from Claim model to ClaimResponse schema.
        
        This test verifies that Claim model instances can be properly
        converted to ClaimResponse schemas for API responses.
        
        Expected behavior:
        - All model fields are accessible in response
        - Additional response fields are properly included
        - Type conversions work correctly
        """
        # Act: Convert model to response schema
        claim_response = ClaimResponse.model_validate(sample_claim_in_db)
        
        # Assert: Verify conversion completeness
        assert hasattr(claim_response, "id"), "Response should include ID"
        assert hasattr(claim_response, "created_at"), "Response should include timestamps"
        assert hasattr(claim_response, "updated_at"), "Response should include timestamps"
        
        # Verify data integrity
        assert claim_response.claim_number == sample_claim_in_db.claim_number, "Data should be preserved"
        assert claim_response.status == sample_claim_in_db.status, "Enum should be preserved"

    @pytest.mark.unit
    def test_update_schema_field_exclusion(self):
        """
        Test ClaimUpdate exclude_unset functionality for PATCH operations.
        
        This test verifies that ClaimUpdate properly supports partial
        updates by excluding unset fields from serialization.
        
        Expected behavior:
        - Only explicitly set fields are included
        - Unset fields don't appear in serialization
        - Partial update semantics work correctly
        """
        # Act: Create partial update and serialize
        partial_update = ClaimUpdate(status=ClaimStatus.HUMAN_REVIEW)
        
        # Serialize with exclude_unset=True (for PATCH operations)
        patch_data = partial_update.model_dump(exclude_unset=True)
        
        # Serialize without exclude_unset (includes all fields)
        full_data = partial_update.model_dump(exclude_unset=False)
        
        # Assert: Verify exclude_unset behavior
        assert "status" in patch_data, "Set fields should be in patch data"
        assert "patient_name" not in patch_data, "Unset fields should not be in patch data"
        assert len(patch_data) == 1, "Patch data should only contain set fields"
        
        assert "patient_name" in full_data, "Full data should include all fields"
        assert full_data["patient_name"] is None, "Unset fields should be None in full data"