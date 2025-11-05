"""Claim model definition."""
import enum
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class ClaimStatus(enum.Enum):
    """Claim processing status enum."""
    
    RECEIVED = "RECEIVED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    OCR_PROCESSING = "OCR_PROCESSING"
    PII_MASKED = "PII_MASKED"
    DQ_VALIDATED = "DQ_VALIDATED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    CONSENT_VERIFIED = "CONSENT_VERIFIED"
    CLAIM_VALIDATED = "CLAIM_VALIDATED"
    PAYER_SUBMITTED = "PAYER_SUBMITTED"
    SETTLED = "SETTLED"
    REJECTED = "REJECTED"
    PROCESSING_ERROR = "PROCESSING_ERROR"


class Claim(BaseModel):
    """
    Claim model representing a medical claim in the system.
    
    This model tracks the complete lifecycle of a claim from initial
    receipt through processing to final settlement or rejection.
    """
    
    __tablename__ = "claims"
    
    # Claim identification and basic info
    claim_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    patient_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Financial information
    claim_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False
    )
    
    # Processing status
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus),
        default=ClaimStatus.RECEIVED,
        nullable=False,
        index=True
    )
    
    # Document and data storage
    document_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="GCS path to the claim document"
    )
    
    # JSON fields for flexible data storage
    raw_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Raw OCR output and extracted data"
    )
    claim_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional metadata and processing information"
    )
    
    # OCR-specific fields
    ocr_confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Overall confidence score from OCR processing (0.0-1.0)"
    )
    ocr_processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when OCR processing completed"
    )
    requires_human_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Flag indicating if claim requires human review due to low confidence or errors"
    )
    
    # Database indexes for performance
    __table_args__ = (
        Index("idx_claim_status_created", "status", "created_at"),
        Index("idx_claim_patient_status", "patient_name", "status"),
    )
    
    def __repr__(self) -> str:
        """String representation of the claim."""
        status_value = self.status.value if hasattr(self.status, 'value') else self.status
        return (
            f"<Claim(id={self.id}, claim_number='{self.claim_number}', "
            f"status='{status_value}', amount={self.claim_amount})>"
        )