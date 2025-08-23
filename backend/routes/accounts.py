from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from dataModels.account import (
    Account, AccountCreate, AccountUpdate, AccountResponse, 
    AccountListResponse, AccountSearchParams, AccountStatus
)
from db.account import AccountDB

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse, status_code=201)
async def create_account(account_data: AccountCreate):
    """Create a new account (one per user) - account number is auto-generated"""
    try:
        # Check if user already has an account
        existing_account = await AccountDB.get_account_by_user_id(account_data.user_id)
        if existing_account:
            raise HTTPException(status_code=400, detail="User already has an account")
        
        account = await AccountDB.create_account(account_data)
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=AccountListResponse)
async def list_accounts(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    account_number: Optional[str] = Query(None, description="Filter by account number (partial match)"),
    status: Optional[AccountStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of accounts per page")
):
    """Get all accounts with filtering and pagination"""
    try:
        search_params = AccountSearchParams(
            user_id=user_id,
            account_number=account_number,
            status=status,
            page=page,
            page_size=page_size
        )
        
        result = await AccountDB.list_accounts(search_params)
        return AccountListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str):
    """Get a specific account by ID"""
    try:
        account = await AccountDB.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/user/{user_id}", response_model=AccountResponse)
async def get_account_by_user_id(user_id: str):
    """Get account by user ID (one account per user)"""
    try:
        account = await AccountDB.get_account_by_user_id(user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found for this user")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/number/{account_number}", response_model=AccountResponse)
async def get_account_by_number(account_number: str):
    """Get account by account number"""
    try:
        account = await AccountDB.get_account_by_account_number(account_number)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: str, account_data: AccountUpdate):
    """Update an account"""
    try:
        # Check if account exists
        existing_account = await AccountDB.get_account_by_id(account_id)
        if not existing_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check for unique constraints if account_number is being updated
        if account_data.account_number and account_data.account_number != existing_account.account_number:
            if await AccountDB.account_exists(account_number=account_data.account_number):
                raise HTTPException(status_code=400, detail="Account number already exists")
        
        updated_account = await AccountDB.update_account(account_id, account_data)
        if not updated_account:
            raise HTTPException(status_code=500, detail="Failed to update account")
        
        return updated_account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{account_id}")
async def delete_account(account_id: str):
    """Delete an account"""
    try:
        # Check if account exists
        existing_account = await AccountDB.get_account_by_id(account_id)
        if not existing_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        success = await AccountDB.delete_account(account_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete account")
        
        return {"message": "Account deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/{account_id}/status", response_model=AccountResponse)
async def update_account_status(account_id: str, status: AccountStatus):
    """Update account status"""
    try:
        # Check if account exists
        existing_account = await AccountDB.get_account_by_id(account_id)
        if not existing_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        updated_account = await AccountDB.update_account_status(account_id, status.value)
        if not updated_account:
            raise HTTPException(status_code=500, detail="Failed to update account status")
        
        return updated_account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/{account_id}/close", response_model=AccountResponse)
async def close_account(account_id: str):
    """Close an account"""
    try:
        # Check if account exists
        existing_account = await AccountDB.get_account_by_id(account_id)
        if not existing_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        closed_account = await AccountDB.close_account(account_id)
        if not closed_account:
            raise HTTPException(status_code=500, detail="Failed to close account")
        
        return closed_account
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{account_id}/exists")
async def check_account_exists(account_id: str):
    """Check if an account exists"""
    try:
        account = await AccountDB.get_account_by_id(account_id)
        return {"exists": account is not None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
