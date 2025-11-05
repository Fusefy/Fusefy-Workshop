"""Pydantic schemas for Claim API."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.models.claim import ClaimStatus


class ClaimStatusSchema(BaseModel):
    """Claim status enum schema."""
    
    model_config = ConfigDict(use_enum_values=True)


class ClaimBase(BaseModel):
    """Base claim schema with common fields."""
    
    claim_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique claim identifier"
    )
    patient_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Patient full name"
    )
    claim_amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Claim amount in dollars"
    )
    document_url: Optional[str] = Field(
        None,
        description="GCS path to claim document"
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw OCR output and extracted data"
    )
    claim_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata and processing information"
    )
    ocr_confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Overall OCR confidence score (0.0-1.0)"
    )
    requires_human_review: Optional[bool] = Field(
        None,
        description="Flag indicating if claim requires human review"
    )


class ClaimCreate(ClaimBase):
    """Schema for creating a new claim."""
    
    status: Optional[ClaimStatus] = Field(
        default=ClaimStatus.RECEIVED,
        description="Initial claim status"
    )


class ClaimUpdate(BaseModel):
    """Schema for updating an existing claim."""
    
    patient_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Patient full name"
    )
    claim_amount: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Claim amount in dollars"
    )
    status: Optional[ClaimStatus] = Field(
        None,
        description="Claim processing status"
    )
    document_url: Optional[str] = Field(
        None,
        description="GCS path to claim document"
    )
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw OCR output and extracted data"
    )
    claim_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata and processing information"
    )


class ClaimResponse(ClaimBase):
    """Schema for claim API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(description="Unique claim ID")
    status: ClaimStatus = Field(description="Current claim status")
    created_at: datetime = Field(description="Claim creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    ocr_processed_at: Optional[datetime] = Field(
        None,
        description="OCR processing completion timestamp"
    )


class ClaimListResponse(BaseModel):
    """Schema for paginated claim list responses."""
    
    claims: List[ClaimResponse] = Field(description="List of claims")
    total: int = Field(description="Total number of claims")
    page: int = Field(description="Current page number")
    size: int = Field(description="Page size")
    pages: int = Field(description="Total number of pages")


class ClaimStatusFilter(BaseModel):
    """Schema for claim status filtering."""
    
    status: ClaimStatus = Field(description="Status to filter by")


# Export the ClaimStatus enum for use in API
__all__ = [
    "ClaimBase",
    "ClaimCreate", 
    "ClaimUpdate",
    "ClaimResponse",
    "ClaimListResponse",
    "ClaimStatusFilter",
    "ClaimStatus",
]