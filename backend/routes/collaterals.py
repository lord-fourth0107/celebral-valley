from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from dataModels.collateral import (
    Collateral, CollateralCreate, CollateralCreateSimple, CollateralUpdate, CollateralResponse, 
    CollateralListResponse, CollateralSearchParams, CollateralStatus, CollateralApproveRequest, CollateralCreateRequest
)
from db.collateral import CollateralDB
from db.user import UserDB

router = APIRouter(prefix="/collaterals", tags=["collaterals"])


@router.post("/", response_model=CollateralResponse, status_code=201)
async def create_collateral(collateral_data: CollateralCreateRequest):
    """Create a new collateral with basic info and mocked data"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(collateral_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # TODO: Process the collateral creation
        # This would typically involve:
        # 1. Image analysis and valuation
        # 2. Risk assessment
        # 3. Loan limit calculation
        # 4. Interest rate determination
        # 5. Due date calculation
        
        # For now, mock the rest of the data
        collateral = await CollateralDB.create_collateral_simple(CollateralCreateSimple(
            user_id=collateral_data.user_id
        ))
        
        # Update the collateral with the provided data
        update_data = CollateralUpdate(
            images=collateral_data.images,
            metadata={
                "name": collateral_data.name,
                "description": collateral_data.description,
                "original_images": collateral_data.images,
                "status": "awaiting_processing"
            }
        )
        
        updated_collateral = await CollateralDB.update_collateral(collateral.id, update_data)
        return updated_collateral
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/{collateral_id}/approve", response_model=CollateralResponse)
async def approve_collateral(collateral_id: str, approve_request: CollateralApproveRequest):
    """Approve a collateral and create a loan transaction"""
    try:
        # Check if collateral exists
        existing_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not existing_collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        approved_collateral = await CollateralDB.approve_collateral(collateral_id, approve_request)
        return approved_collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=CollateralListResponse)
async def list_collaterals(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[CollateralStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of collaterals per page")
):
    """Get all collaterals with filtering and pagination"""
    try:
        search_params = CollateralSearchParams(
            user_id=user_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        result = await CollateralDB.list_collaterals(search_params)
        return CollateralListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{collateral_id}", response_model=CollateralResponse)
async def get_collateral(collateral_id: str):
    """Get a specific collateral by ID"""
    try:
        collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        return collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{collateral_id}", response_model=CollateralResponse)
async def update_collateral(collateral_id: str, collateral_data: CollateralUpdate):
    """Update a collateral"""
    try:
        # Check if collateral exists
        existing_collateral = await CollateralDB.get_collateral_by_id(collateral_id)
        if not existing_collateral:
            raise HTTPException(status_code=404, detail="Collateral not found")
        
        updated_collateral = await CollateralDB.update_collateral(collateral_id, collateral_data)
        if not updated_collateral:
            raise HTTPException(status_code=500, detail="Failed to update collateral")
        
        return updated_collateral
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
