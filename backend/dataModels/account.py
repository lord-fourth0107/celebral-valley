from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class AccountBase(BaseModel):
    """Base account model with common fields"""
    user_id: str = Field(..., title="User ID", description="ID of the user who owns this account")


class AccountCreate(AccountBase):
    """Model for creating a new account - account_number is auto-generated"""
    pass


class AccountUpdate(BaseModel):
    """Model for updating an account - all fields optional"""
    account_number: Optional[str] = Field(None, title="Account Number", description="Unique account number", min_length=1, max_length=50)
    status: Optional[AccountStatus] = Field(None, title="Status", description="Account status")
    closed_at: Optional[datetime] = Field(None, title="Closed At", description="When the account was closed")


class Account(AccountBase):
    """Complete account model with all fields"""
    id: str = Field(..., title="Account ID", description="Unique identifier for the account")
    account_number: str = Field(..., title="Account Number", description="Unique account number", min_length=1, max_length=50)
    status: AccountStatus = Field(default=AccountStatus.ACTIVE, title="Status", description="Account status")
    created_at: datetime = Field(..., title="Created At", description="Account creation timestamp")
    updated_at: datetime = Field(..., title="Updated At", description="Last update timestamp")
    closed_at: Optional[datetime] = Field(None, title="Closed At", description="When the account was closed")

    class Config:
        from_attributes = True


class AccountResponse(Account):
    """Account response model - same as Account but for API responses"""
    pass


class AccountListResponse(BaseModel):
    """Response model for listing accounts"""
    accounts: list[Account] = Field(..., title="Accounts", description="List of accounts")
    total: int = Field(..., title="Total", description="Total number of accounts")
    page: int = Field(..., title="Page", description="Current page number")
    page_size: int = Field(..., title="Page Size", description="Number of accounts per page")


class AccountSearchParams(BaseModel):
    """Parameters for searching/filtering accounts"""
    user_id: Optional[str] = Field(None, title="User ID", description="Filter by user ID")
    account_number: Optional[str] = Field(None, title="Account Number", description="Filter by account number (partial match)")
    status: Optional[AccountStatus] = Field(None, title="Status", description="Filter by status")
    page: int = Field(default=1, title="Page", description="Page number", ge=1)
    page_size: int = Field(default=20, title="Page Size", description="Number of accounts per page", ge=1, le=100)
