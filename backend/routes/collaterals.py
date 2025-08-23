from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from dataModels.collateral import (
    Collateral, CollateralCreate, CollateralUpdate, CollateralResponse, 
    CollateralListResponse, CollateralSearchParams, CollateralStatus
)
from db.collateral import CollateralDB
from db.user import UserDB

router = APIRouter(prefix="/collaterals", tags=["collaterals"])


@router.post("/", response_model=CollateralResponse, status_code=201)
async def create_collateral(collateral_data: CollateralCreate):
    """Create a new collateral"""
    try:
        # Validate user exists
        user = await UserDB.get_user_by_id(collateral_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        collateral = await CollateralDB.create_collateral(collateral_data)
        return collateral
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
