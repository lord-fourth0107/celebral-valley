from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class CollateralStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"
    DEFAULTED = "defaulted"


class CollateralBase(BaseModel):
    """Base collateral model with common fields"""
    user_id: str = Field(..., title="User ID", description="ID of the user who owns this collateral")
    loan_amount: Decimal = Field(..., title="Loan Amount", description="Amount of loan against this collateral", gt=0)
    loan_limit: Decimal = Field(..., title="Loan Limit", description="Maximum loan amount allowed against this collateral", gt=0)
    interest: Decimal = Field(..., title="Interest", description="Interest rate for the loan against this collateral")
    due_date: datetime = Field(..., title="Due Date", description="Due date for the collateral loan")
    image_paths: Optional[List[str]] = Field([], title="Image Paths", description="Paths to the collateral images")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional collateral metadata")


class CollateralCreate(CollateralBase):
    """Model for creating a new collateral"""
    pass


class CollateralUpdate(BaseModel):
    """Model for updating a collateral - all fields optional"""
    loan_amount: Optional[Decimal] = Field(None, title="Loan Amount", description="Amount of loan against this collateral", gt=0)
    loan_limit: Optional[Decimal] = Field(None, title="Loan Limit", description="Maximum loan amount allowed against this collateral", gt=0)
    interest: Optional[Decimal] = Field(None, title="Interest", description="Interest rate for the loan against this collateral")
    due_date: Optional[datetime] = Field(None, title="Due Date", description="Due date for the collateral loan")
    status: Optional[CollateralStatus] = Field(None, title="Status", description="Collateral status")
    image_paths: Optional[List[str]] = Field(None, title="Image Paths", description="Paths to the collateral images")
    metadata: Optional[dict] = Field(None, title="Metadata", description="Additional collateral metadata")


class Collateral(CollateralBase):
    """Complete collateral model with all fields"""
    id: str = Field(..., title="Collateral ID", description="Unique identifier for the collateral")
    status: CollateralStatus = Field(default=CollateralStatus.PENDING, title="Status", description="Collateral status")
    created_at: datetime = Field(..., title="Created At", description="Collateral creation timestamp")
    updated_at: datetime = Field(..., title="Updated At", description="Last update timestamp")

    class Config:
        from_attributes = True


class CollateralResponse(Collateral):
    """Collateral response model - same as Collateral but for API responses"""
    pass


class CollateralListResponse(BaseModel):
    """Response model for listing collaterals"""
    collaterals: list[Collateral] = Field(..., title="Collaterals", description="List of collaterals")
    total: int = Field(..., title="Total", description="Total number of collaterals")
    page: int = Field(..., title="Page", description="Current page number")
    page_size: int = Field(..., title="Page Size", description="Number of collaterals per page")


class CollateralSearchParams(BaseModel):
    """Parameters for searching/filtering collaterals"""
    user_id: Optional[str] = Field(None, title="User ID", description="Filter by user ID")
    status: Optional[CollateralStatus] = Field(None, title="Status", description="Filter by status")
    page: int = Field(default=1, title="Page", description="Page number", ge=1)
    page_size: int = Field(default=20, title="Page Size", description="Number of collaterals per page", ge=1, le=100)
