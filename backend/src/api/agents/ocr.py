"""
API endpoints for OCR Agent operations.

This module provides REST API endpoints for triggering OCR processing
on uploaded documents using the ADK-based OCR agent.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.ocr_agent import ocr_agent
from src.config.database import get_db
from src.models.claim import Claim, ClaimStatus
from src.schemas.claim import ClaimResponse, ClaimUpdate
from src.utils.gcs_helper import gcs_manager

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/agents/ocr",
    tags=["OCR Agent"],
    responses={
        404: {"description": "Claim not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/process/{claim_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Process document with OCR agent",
    description="""
    Upload and process a document using the ADK-based OCR agent.
    
    This endpoint accepts document uploads and triggers the complete OCR processing pipeline:
    - Validates document format (PDF, PNG, JPG, TIFF)
    - Uploads document to Google Cloud Storage
    - Extracts text using Google Document AI or Vision API
    - Structures extracted data using ADK agent intelligence
    - Updates claim status and stores results
    - Determines if human review is required
    
    The processing is performed asynchronously for large documents.
    """
)
async def process_document(
    claim_id: UUID,
    file: UploadFile = File(..., description="Document file to process (PDF, PNG, JPG, TIFF)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process an uploaded document with the OCR agent.
    
    Args:
        claim_id: UUID of the claim to associate with the document
        file: Uploaded document file
        db: Database session
        
    Returns:
        Processing results including extracted data and confidence scores
        
    Raises:
        HTTPException: If claim not found, file invalid, or processing fails
    """
    try:
        # Validate claim exists
        claim = await db.get(Claim, claim_id)
        if not claim:
            logger.warning(f"Claim not found: {claim_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )
        
        # Check if claim is in a valid state for OCR processing
        if claim.status not in [ClaimStatus.RECEIVED, ClaimStatus.DOCUMENT_UPLOADED]:
            logger.warning(f"Invalid claim status for OCR: {claim.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Claim status '{claim.status.value}' is not valid for OCR processing"
            )
        
        # Validate file format before processing
        supported_formats = [
            "application/pdf",
            "image/png",
            "image/jpeg", 
            "image/jpg",
            "image/tiff",
            "image/tif"
        ]
        
        if file.content_type not in supported_formats:
            logger.warning(f"Unsupported file format: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {file.content_type}. "
                       f"Supported formats: {', '.join(supported_formats)}"
            )
        
        # Log processing start
        logger.info(f"Starting OCR processing for claim {claim_id}, file: {file.filename}")
        
        # Update claim status to indicate processing has started
        claim.status = ClaimStatus.OCR_PROCESSING
        await db.commit()
        
        # Process document with OCR agent
        processing_result = await ocr_agent.process_document(file, claim_id)
        
        # Update claim with OCR results
        update_data = {
            "document_url": processing_result["gcs_uri"],
            "raw_data": {
                "extracted_text": processing_result["extracted_text"],
                "structured_data": processing_result["structured_data"],
                "confidence_scores": processing_result["confidence_scores"],
                "ocr_metadata": processing_result["ocr_metadata"]
            },
            "ocr_confidence_score": processing_result["overall_confidence"],
            "ocr_processed_at": datetime.utcnow(),
            "requires_human_review": processing_result["requires_human_review"]
        }
        
        # Update claim status based on processing results
        if processing_result["requires_human_review"]:
            update_data["status"] = ClaimStatus.HUMAN_REVIEW
        else:
            update_data["status"] = ClaimStatus.DQ_VALIDATED
        
        # Apply updates to claim
        for field, value in update_data.items():
            if hasattr(claim, field):
                setattr(claim, field, value)
        
        await db.commit()
        await db.refresh(claim)
        
        # Log successful completion
        logger.info(
            f"OCR processing completed for claim {claim_id}. "
            f"Status: {claim.status.value}, "
            f"Confidence: {processing_result['overall_confidence']:.2f}, "
            f"Human review: {processing_result['requires_human_review']}"
        )
        
        # Prepare response
        response_data = {
            "claim_id": str(claim_id),
            "processing_status": "completed",
            "claim_status": claim.status.value,
            "document_url": processing_result["gcs_uri"],
            "extracted_data": processing_result["structured_data"],
            "confidence_score": processing_result["overall_confidence"],
            "requires_human_review": processing_result["requires_human_review"],
            "processing_metadata": processing_result["ocr_metadata"],
            "message": "Document processed successfully"
        }
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log unexpected errors and update claim status
        logger.error(f"OCR processing failed for claim {claim_id}: {e}")
        
        try:
            # Update claim status to indicate processing failed
            if 'claim' in locals():
                claim.status = ClaimStatus.PROCESSING_ERROR
                claim.requires_human_review = True
                await db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update claim status after error: {db_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.get(
    "/status/{claim_id}",
    response_model=Dict[str, Any],
    summary="Get OCR processing status",
    description="""
    Get the current OCR processing status for a claim.
    
    Returns information about document processing status, confidence scores,
    extracted data, and whether human review is required.
    """
)
async def get_ocr_status(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get OCR processing status for a claim.
    
    Args:
        claim_id: UUID of the claim to check
        db: Database session
        
    Returns:
        OCR processing status and results
        
    Raises:
        HTTPException: If claim not found
    """
    try:
        # Get claim
        claim = await db.get(Claim, claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )
        
        # Prepare status response
        status_data = {
            "claim_id": str(claim_id),
            "current_status": claim.status.value,
            "ocr_processed": claim.ocr_processed_at is not None,
            "ocr_processed_at": claim.ocr_processed_at.isoformat() if claim.ocr_processed_at else None,
            "confidence_score": claim.ocr_confidence_score,
            "requires_human_review": claim.requires_human_review,
            "document_url": claim.document_url,
        }
        
        # Add extracted data if available
        if claim.raw_data:
            status_data["extracted_data"] = claim.raw_data.get("structured_data", {})
            status_data["ocr_metadata"] = claim.raw_data.get("ocr_metadata", {})
        
        return status_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get OCR status for claim {claim_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve OCR status: {str(e)}"
        )


@router.get(
    "/documents/{claim_id}",
    response_model=Dict[str, Any],
    summary="List claim documents",
    description="""
    List all documents associated with a claim stored in Google Cloud Storage.
    
    Returns metadata for all documents including file names, sizes, upload timestamps,
    and signed URLs for secure access.
    """
)
async def list_claim_documents(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    include_signed_urls: bool = False
) -> Dict[str, Any]:
    """
    List documents associated with a claim.
    
    Args:
        claim_id: UUID of the claim
        db: Database session
        include_signed_urls: Whether to generate signed URLs for document access
        
    Returns:
        List of document metadata
        
    Raises:
        HTTPException: If claim not found or GCS access fails
    """
    try:
        # Validate claim exists
        claim = await db.get(Claim, claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )
        
        # Get documents from GCS
        documents = gcs_manager.list_claim_documents(claim_id)
        
        # Add signed URLs if requested
        if include_signed_urls:
            for doc in documents:
                blob_name = doc['name']
                signed_url = gcs_manager.generate_signed_url(blob_name)
                doc['signed_url'] = signed_url
        
        return {
            "claim_id": str(claim_id),
            "document_count": len(documents),
            "documents": documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents for claim {claim_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete(
    "/documents/{claim_id}/{document_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete claim document",
    description="""
    Delete a specific document associated with a claim from Google Cloud Storage.
    
    This operation cannot be undone. Use with caution.
    """
)
async def delete_claim_document(
    claim_id: UUID,
    document_name: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a document associated with a claim.
    
    Args:
        claim_id: UUID of the claim
        document_name: Name of the document to delete
        db: Database session
        
    Raises:
        HTTPException: If claim not found or deletion fails
    """
    try:
        # Validate claim exists
        claim = await db.get(Claim, claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )
        
        # Construct blob name
        blob_name = f"claims/{claim_id}/{document_name}"
        
        # Delete from GCS
        success = gcs_manager.delete_blob(blob_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{document_name}' not found"
            )
        
        # Update claim if this was the primary document
        if claim.document_url and blob_name in claim.document_url:
            claim.document_url = None
            await db.commit()
        
        logger.info(f"Deleted document {document_name} for claim {claim_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_name} for claim {claim_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post(
    "/reprocess/{claim_id}",
    response_model=Dict[str, Any],
    summary="Reprocess claim with OCR agent",
    description="""
    Reprocess an existing claim's documents with the OCR agent.
    
    This endpoint can be used to reprocess documents when:
    - OCR confidence was initially low
    - Processing failed previously
    - Agent improvements require reprocessing
    """
)
async def reprocess_claim(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Reprocess a claim's documents with the OCR agent.
    
    Args:
        claim_id: UUID of the claim to reprocess
        db: Database session
        
    Returns:
        Reprocessing results
        
    Raises:
        HTTPException: If claim not found or no documents available
    """
    try:
        # Get claim
        claim = await db.get(Claim, claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )
        
        # Check if claim has documents to reprocess
        if not claim.document_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents available for reprocessing"
            )
        
        # Get document from GCS
        blob_name = claim.document_url.replace(f"gs://{gcs_manager.bucket_name}/", "")
        document_content = gcs_manager.get_blob_content(blob_name)
        
        if not document_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original document not found in storage"
            )
        
        # Create a mock UploadFile for reprocessing
        # Note: In a real implementation, you might want to store original file metadata
        from io import BytesIO
        from fastapi import UploadFile
        
        # Get document metadata
        doc_metadata = gcs_manager.get_blob_metadata(blob_name)
        if not doc_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document metadata not found"
            )
        
        # Create UploadFile-like object
        file_obj = BytesIO(document_content)
        mock_file = UploadFile(
            file=file_obj,
            filename=blob_name.split('/')[-1],
            size=len(document_content),
            headers={"content-type": doc_metadata['content_type']}
        )
        
        # Update claim status
        claim.status = ClaimStatus.OCR_PROCESSING
        await db.commit()
        
        # Reprocess with OCR agent
        processing_result = await ocr_agent.process_document(mock_file, claim_id)
        
        # Update claim with new results
        claim.raw_data = {
            "extracted_text": processing_result["extracted_text"],
            "structured_data": processing_result["structured_data"],
            "confidence_scores": processing_result["confidence_scores"],
            "ocr_metadata": processing_result["ocr_metadata"]
        }
        claim.ocr_confidence_score = processing_result["overall_confidence"]
        claim.ocr_processed_at = datetime.utcnow()
        claim.requires_human_review = processing_result["requires_human_review"]
        
        # Update status based on results
        if processing_result["requires_human_review"]:
            claim.status = ClaimStatus.HUMAN_REVIEW
        else:
            claim.status = ClaimStatus.DQ_VALIDATED
        
        await db.commit()
        
        logger.info(f"Reprocessed claim {claim_id} with confidence {processing_result['overall_confidence']:.2f}")
        
        return {
            "claim_id": str(claim_id),
            "reprocessing_status": "completed",
            "new_confidence_score": processing_result["overall_confidence"],
            "requires_human_review": processing_result["requires_human_review"],
            "claim_status": claim.status.value,
            "message": "Claim reprocessed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess claim {claim_id}: {e}")
        
        # Update claim status on failure
        try:
            if 'claim' in locals():
                claim.status = ClaimStatus.PROCESSING_ERROR
                claim.requires_human_review = True
                await db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reprocessing failed: {str(e)}"
        )