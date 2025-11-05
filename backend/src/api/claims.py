"""Claims API endpoints with CRUD operations."""
import math
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.models.claim import Claim, ClaimStatus
from src.schemas.claim import (
    ClaimCreate,
    ClaimListResponse,
    ClaimResponse,
    ClaimUpdate,
)

router = APIRouter()


@router.post(
    "/claims",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new claim",
    description="Create a new medical claim in the system"
)
async def create_claim(
    claim_data: ClaimCreate,
    db: AsyncSession = Depends(get_db)
) -> ClaimResponse:
    """
    Create a new claim with the provided information.
    
    Args:
        claim_data: The claim data to create
        db: Database session dependency
        
    Returns:
        The created claim data
        
    Raises:
        HTTPException: If claim number already exists (409)
    """
    try:
        # Check if claim number already exists
        existing_claim = await db.execute(
            select(Claim).where(Claim.claim_number == claim_data.claim_number)
        )
        if existing_claim.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Claim with number '{claim_data.claim_number}' already exists"
            )
        
        # Create new claim
        db_claim = Claim(**claim_data.model_dump())
        db.add(db_claim)
        await db.commit()
        await db.refresh(db_claim)
        
        return ClaimResponse.model_validate(db_claim)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create claim: {str(e)}"
        )


@router.get(
    "/claims",
    response_model=ClaimListResponse,
    summary="List all claims with pagination",
    description="Retrieve a paginated list of all claims in the system"
)
async def list_claims(
    page: int = Query(1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    db: AsyncSession = Depends(get_db)
) -> ClaimListResponse:
    """
    Get a paginated list of all claims.
    
    Args:
        page: Page number (1-based)
        size: Number of items per page
        db: Database session dependency
        
    Returns:
        Paginated list of claims
    """
    try:
        # Handle invalid page numbers gracefully - default to page 1
        if page < 1:
            page = 1
            
        # Handle invalid size values gracefully - cap at maximum
        if size > 100:
            size = 100
        elif size < 1:
            size = 1
            
        # Calculate offset
        offset = (page - 1) * size
        
        # Get total count
        count_query = select(func.count(Claim.id))
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Get claims for current page
        claims_query = (
            select(Claim)
            .order_by(Claim.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        claims_result = await db.execute(claims_query)
        claims = claims_result.scalars().all()
        
        # Calculate total pages
        pages = math.ceil(total / size) if total > 0 else 0
        
        return ClaimListResponse(
            claims=[ClaimResponse.model_validate(claim) for claim in claims],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve claims: {str(e)}"
        )


@router.get(
    "/claims/{claim_id}",
    response_model=ClaimResponse,
    summary="Get claim by ID",
    description="Retrieve a specific claim by its unique identifier"
)
async def get_claim(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> ClaimResponse:
    """
    Get a specific claim by ID.
    
    Args:
        claim_id: The unique identifier of the claim
        db: Database session dependency
        
    Returns:
        The claim data
        
    Raises:
        HTTPException: If claim not found (404)
    """
    try:
        query = select(Claim).where(Claim.id == claim_id)
        result = await db.execute(query)
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID '{claim_id}' not found"
            )
        
        return ClaimResponse.model_validate(claim)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve claim: {str(e)}"
        )


@router.patch(
    "/claims/{claim_id}",
    response_model=ClaimResponse,
    summary="Update claim",
    description="Update specific fields of an existing claim"
)
async def update_claim(
    claim_id: uuid.UUID,
    claim_update: ClaimUpdate,
    db: AsyncSession = Depends(get_db)
) -> ClaimResponse:
    """
    Update an existing claim with new data.
    
    Args:
        claim_id: The unique identifier of the claim
        claim_update: The fields to update
        db: Database session dependency
        
    Returns:
        The updated claim data
        
    Raises:
        HTTPException: If claim not found (404)
    """
    try:
        # Find the existing claim
        query = select(Claim).where(Claim.id == claim_id)
        result = await db.execute(query)
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID '{claim_id}' not found"
            )
        
        # Update only provided fields
        update_data = claim_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(claim, field, value)
        
        await db.commit()
        await db.refresh(claim)
        
        return ClaimResponse.model_validate(claim)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim: {str(e)}"
        )


@router.get(
    "/claims/status/{status}",
    response_model=List[ClaimResponse],
    summary="Filter claims by status",
    description="Retrieve all claims with a specific processing status"
)
async def get_claims_by_status(
    status: ClaimStatus,
    db: AsyncSession = Depends(get_db)
) -> List[ClaimResponse]:
    """
    Get all claims filtered by processing status.
    
    Args:
        status: The claim status to filter by
        db: Database session dependency
        
    Returns:
        List of claims with the specified status
    """
    try:
        query = (
            select(Claim)
            .where(Claim.status == status)
            .order_by(Claim.created_at.desc())
        )
        result = await db.execute(query)
        claims = result.scalars().all()
        
        return [ClaimResponse.model_validate(claim) for claim in claims]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve claims by status: {str(e)}"
        )