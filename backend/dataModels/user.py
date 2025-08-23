from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    VERIFIER = "verifier"
    ORGANIZATION = "organization"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., title="Email", description="User's email address")
    username: str = Field(..., title="Username", description="Unique username for the user", min_length=3, max_length=50)
    first_name: str = Field(..., title="First Name", description="User's first name", min_length=1, max_length=100)
    last_name: str = Field(..., title="Last Name", description="User's last name", min_length=1, max_length=100)
    phone: Optional[str] = Field(None, title="Phone", description="User's phone number")
    date_of_birth: Optional[datetime] = Field(None, title="Date of Birth", description="User's date of birth")
    address: Optional[str] = Field(None, title="Address", description="User's residential address")
    city: Optional[str] = Field(None, title="City", description="User's city")
    state: Optional[str] = Field(None, title="State", description="User's state/province")
    country: Optional[str] = Field(None, title="Country", description="User's country")
    postal_code: Optional[str] = Field(None, title="Postal Code", description="User's postal code")
    role: UserRole = Field(default=UserRole.USER, title="Role", description="User's role in the system")


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Model for updating a user - all fields optional"""
    email: Optional[EmailStr] = Field(None, title="Email", description="User's email address")
    username: Optional[str] = Field(None, title="Username", description="Unique username for the user", min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, title="First Name", description="User's first name", min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, title="Last Name", description="User's last name", min_length=1, max_length=100)
    phone: Optional[str] = Field(None, title="Phone", description="User's phone number")
    date_of_birth: Optional[datetime] = Field(None, title="Date of Birth", description="User's date of birth")
    address: Optional[str] = Field(None, title="Address", description="User's residential address")
    city: Optional[str] = Field(None, title="City", description="User's city")
    state: Optional[str] = Field(None, title="State", description="User's state/province")
    country: Optional[str] = Field(None, title="Country", description="User's country")
    postal_code: Optional[str] = Field(None, title="Postal Code", description="User's postal code")
    role: Optional[UserRole] = Field(None, title="Role", description="User's role in the system")
    status: Optional[UserStatus] = Field(None, title="Status", description="User's account status")
    kyc_verified: Optional[bool] = Field(None, title="KYC Verified", description="Whether user's KYC is verified")


class User(UserBase):
    """Complete user model with all fields"""
    id: str = Field(..., title="User ID", description="Unique identifier for the user")
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION, title="Status", description="User's account status")
    kyc_verified: bool = Field(default=False, title="KYC Verified", description="Whether user's KYC is verified")
    created_at: datetime = Field(..., title="Created At", description="Account creation timestamp")
    updated_at: datetime = Field(..., title="Updated At", description="Last update timestamp")

    class Config:
        from_attributes = True


class UserResponse(User):
    """User response model - same as User but for API responses"""
    pass


class UserListResponse(BaseModel):
    """Response model for listing users"""
    users: List[User] = Field(..., title="Users", description="List of users")
    total: int = Field(..., title="Total", description="Total number of users")
    page: int = Field(..., title="Page", description="Current page number")
    page_size: int = Field(..., title="Page Size", description="Number of users per page")


class UserSearchParams(BaseModel):
    """Parameters for searching/filtering users"""
    email: Optional[str] = Field(None, title="Email", description="Filter by email (partial match)")
    username: Optional[str] = Field(None, title="Username", description="Filter by username (partial match)")
    status: Optional[UserStatus] = Field(None, title="Status", description="Filter by status")
    role: Optional[UserRole] = Field(None, title="Role", description="Filter by role")
    kyc_verified: Optional[bool] = Field(None, title="KYC Verified", description="Filter by KYC verification status")
    page: int = Field(default=1, title="Page", description="Page number", ge=1)
    page_size: int = Field(default=20, title="Page Size", description="Number of users per page", ge=1, le=100)

