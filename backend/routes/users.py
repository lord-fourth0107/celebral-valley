from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from dataModels.user import (
    User, UserCreate, UserUpdate, UserResponse, 
    UserListResponse, UserSearchParams, UserStatus
)
from db.user import UserDB

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        if await UserDB.user_exists(email=user_data.email):
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        if await UserDB.user_exists(username=user_data.username):
            raise HTTPException(status_code=400, detail="User with this username already exists")
        
        user = await UserDB.create_user(user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=UserListResponse)
async def list_users(
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    username: Optional[str] = Query(None, description="Filter by username (partial match)"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    kyc_verified: Optional[bool] = Query(None, description="Filter by KYC verification status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of users per page")
):
    """Get all users with filtering and pagination"""
    try:
        search_params = UserSearchParams(
            email=email,
            username=username,
            status=status,
            kyc_verified=kyc_verified,
            page=page,
            page_size=page_size
        )
        
        result = await UserDB.list_users(search_params)
        return UserListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific user by ID"""
    try:
        user = await UserDB.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update a user"""
    try:
        # Check if user exists
        existing_user = await UserDB.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for unique constraints if email or username is being updated
        if user_data.email and user_data.email != existing_user.email:
            if await UserDB.user_exists(email=user_data.email, exclude_user_id=user_id):
                raise HTTPException(status_code=400, detail="User with this email already exists")
        
        if user_data.username and user_data.username != existing_user.username:
            if await UserDB.user_exists(username=user_data.username, exclude_user_id=user_id):
                raise HTTPException(status_code=400, detail="User with this username already exists")
        
        updated_user = await UserDB.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update user")
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        # Check if user exists
        existing_user = await UserDB.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await UserDB.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get a user by email"""
    try:
        user = await UserDB.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    """Get a user by username"""
    try:
        user = await UserDB.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(user_id: str, status: UserStatus):
    """Update user status"""
    try:
        # Check if user exists
        existing_user = await UserDB.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = await UserDB.update_user_status(user_id, status.value)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update user status")
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.patch("/{user_id}/kyc", response_model=UserResponse)
async def update_kyc_status(user_id: str, kyc_verified: bool):
    """Update user KYC verification status"""
    try:
        # Check if user exists
        existing_user = await UserDB.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = await UserDB.update_kyc_status(user_id, kyc_verified)
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to update KYC status")
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{user_id}/exists")
async def check_user_exists(user_id: str):
    """Check if a user exists"""
    try:
        user = await UserDB.get_user_by_id(user_id)
        return {"exists": user is not None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
